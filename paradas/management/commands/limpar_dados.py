"""
Comando para limpeza de dados do sistema BusFeed

Este comando remove dados do banco de forma segura e controlada,
com opções para limpeza seletiva ou completa.
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
import logging

from paradas.models import Parada
from linhas.models import Linha, LinhaParada
from rotas.models import Rota, RotaLinha, RotaParada
from usuarios.models import Usuario


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Limpa dados do sistema de forma controlada'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tudo',
            action='store_true',
            help='Remove todos os dados do sistema'
        )
        parser.add_argument(
            '--paradas',
            action='store_true',
            help='Remove apenas paradas (e relacionamentos dependentes)'
        )
        parser.add_argument(
            '--linhas',
            action='store_true',
            help='Remove apenas linhas (e relacionamentos dependentes)'
        )
        parser.add_argument(
            '--rotas',
            action='store_true',
            help='Remove apenas rotas calculadas'
        )
        parser.add_argument(
            '--usuarios',
            action='store_true',
            help='Remove dados de usuários (CUIDADO!)'
        )
        parser.add_argument(
            '--relacionamentos',
            action='store_true',
            help='Remove apenas relacionamentos (mantém paradas e linhas)'
        )
        parser.add_argument(
            '--confirmar',
            action='store_true',
            help='Confirma a operação sem prompt interativo'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Exibe informações detalhadas durante a execução'
        )
        parser.add_argument(
            '--backup',
            action='store_true',
            help='Cria backup dos dados antes de limpar (futuro)'
        )

    def handle(self, *args, **options):
        """Executa a limpeza de dados"""
        
        if options['verbose']:
            self.stdout.write(
                self.style.WARNING('🧹 Iniciando limpeza de dados do BusFeed...')
            )

        # Verifica se pelo menos uma opção foi especificada
        opcoes_limpeza = [
            options['tudo'], options['paradas'], options['linhas'],
            options['rotas'], options['usuarios'], options['relacionamentos']
        ]
        
        if not any(opcoes_limpeza):
            raise CommandError(
                'Especifique pelo menos uma opção de limpeza. '
                'Use --help para ver as opções disponíveis.'
            )

        try:
            # Exibe estatísticas antes da limpeza
            if options['verbose']:
                self._exibir_estatisticas_pre_limpeza()

            # Confirma a operação se necessário
            if not options['confirmar']:
                if not self._confirmar_operacao(options):
                    self.stdout.write('❌ Operação cancelada pelo usuário')
                    return

            # Executa a limpeza
            with transaction.atomic():
                dados_removidos = self._executar_limpeza(options)
                
                if options['verbose']:
                    self._exibir_resultado_limpeza(dados_removidos)

                self.stdout.write(
                    self.style.SUCCESS('✅ Limpeza concluída com sucesso!')
                )

        except Exception as e:
            logger.error(f"Erro durante limpeza: {e}")
            raise CommandError(f'Erro na limpeza de dados: {e}')

    def _exibir_estatisticas_pre_limpeza(self):
        """Exibe estatísticas antes da limpeza"""
        self.stdout.write('\n📊 ESTATÍSTICAS ATUAIS:')
        
        stats = {
            'Paradas': Parada.objects.count(),
            'Linhas': Linha.objects.count(),
            'Relacionamentos Linha-Parada': LinhaParada.objects.count(),
            'Rotas': Rota.objects.count(),
            'Relacionamentos Rota-Linha': RotaLinha.objects.count(),
            'Relacionamentos Rota-Parada': RotaParada.objects.count(),
            'Usuários': Usuario.objects.count(),
        }
        
        for item, count in stats.items():
            if count > 0:
                self.stdout.write(f'  📈 {item}: {count}')
            else:
                self.stdout.write(f'  📊 {item}: {count}')

    def _confirmar_operacao(self, options):
        """Confirma a operação com o usuário"""
        self.stdout.write('\n⚠️  ATENÇÃO: Esta operação irá remover dados permanentemente!')
        
        # Lista o que será removido
        acoes = []
        if options['tudo']:
            acoes.append('🗑️  TODOS OS DADOS do sistema')
        else:
            if options['paradas']:
                acoes.append('📍 Paradas e relacionamentos dependentes')
            if options['linhas']:
                acoes.append('🚌 Linhas e relacionamentos dependentes')
            if options['rotas']:
                acoes.append('🗺️  Rotas calculadas')
            if options['usuarios']:
                acoes.append('👤 Dados de usuários')
            if options['relacionamentos']:
                acoes.append('🔗 Relacionamentos (mantendo paradas e linhas)')
        
        self.stdout.write('\nSerá removido:')
        for acao in acoes:
            self.stdout.write(f'  {acao}')
        
        # Solicita confirmação
        resposta = input('\nDeseja continuar? (digite "SIM" para confirmar): ')
        return resposta.upper() == 'SIM'

    def _executar_limpeza(self, options):
        """Executa a limpeza baseada nas opções"""
        dados_removidos = {}
        
        if options['tudo']:
            dados_removidos = self._limpar_tudo(options['verbose'])
        else:
            if options['relacionamentos']:
                dados_removidos.update(self._limpar_relacionamentos(options['verbose']))
            
            if options['rotas']:
                dados_removidos.update(self._limpar_rotas(options['verbose']))
            
            if options['usuarios']:
                dados_removidos.update(self._limpar_usuarios(options['verbose']))
            
            if options['linhas']:
                dados_removidos.update(self._limpar_linhas(options['verbose']))
            
            if options['paradas']:
                dados_removidos.update(self._limpar_paradas(options['verbose']))
        
        return dados_removidos

    def _limpar_tudo(self, verbose=False):
        """Remove todos os dados do sistema"""
        if verbose:
            self.stdout.write('🗑️  Removendo TODOS os dados...')
        
        dados_removidos = {}
        
        # Remove na ordem correta (relacionamentos primeiro)
        dados_removidos['Relacionamentos Rota-Parada'] = RotaParada.objects.count()
        RotaParada.objects.all().delete()
        
        dados_removidos['Relacionamentos Rota-Linha'] = RotaLinha.objects.count()
        RotaLinha.objects.all().delete()
        
        dados_removidos['Rotas'] = Rota.objects.count()
        Rota.objects.all().delete()
        
        dados_removidos['Relacionamentos Linha-Parada'] = LinhaParada.objects.count()
        LinhaParada.objects.all().delete()
        
        dados_removidos['Linhas'] = Linha.objects.count()
        Linha.objects.all().delete()
        
        dados_removidos['Paradas'] = Parada.objects.count()
        Parada.objects.all().delete()
        
        dados_removidos['Usuários'] = Usuario.objects.count()
        Usuario.objects.all().delete()
        
        if verbose:
            self.stdout.write('✅ Todos os dados removidos')
        
        return dados_removidos

    def _limpar_paradas(self, verbose=False):
        """Remove paradas e relacionamentos dependentes"""
        if verbose:
            self.stdout.write('📍 Removendo paradas...')
        
        dados_removidos = {}
        
        # Remove relacionamentos dependentes primeiro
        dados_removidos['Relacionamentos Rota-Parada'] = RotaParada.objects.count()
        RotaParada.objects.all().delete()
        
        dados_removidos['Relacionamentos Linha-Parada'] = LinhaParada.objects.count()
        LinhaParada.objects.all().delete()
        
        # Remove paradas
        dados_removidos['Paradas'] = Parada.objects.count()
        Parada.objects.all().delete()
        
        if verbose:
            self.stdout.write('✅ Paradas removidas')
        
        return dados_removidos

    def _limpar_linhas(self, verbose=False):
        """Remove linhas e relacionamentos dependentes"""
        if verbose:
            self.stdout.write('🚌 Removendo linhas...')
        
        dados_removidos = {}
        
        # Remove relacionamentos dependentes primeiro
        dados_removidos['Relacionamentos Rota-Linha'] = RotaLinha.objects.count()
        RotaLinha.objects.all().delete()
        
        dados_removidos['Relacionamentos Linha-Parada'] = LinhaParada.objects.count()
        LinhaParada.objects.all().delete()
        
        # Remove linhas
        dados_removidos['Linhas'] = Linha.objects.count()
        Linha.objects.all().delete()
        
        if verbose:
            self.stdout.write('✅ Linhas removidas')
        
        return dados_removidos

    def _limpar_rotas(self, verbose=False):
        """Remove rotas calculadas"""
        if verbose:
            self.stdout.write('🗺️  Removendo rotas...')
        
        dados_removidos = {}
        
        # Remove relacionamentos de rotas primeiro
        dados_removidos['Relacionamentos Rota-Parada'] = RotaParada.objects.count()
        RotaParada.objects.all().delete()
        
        dados_removidos['Relacionamentos Rota-Linha'] = RotaLinha.objects.count()
        RotaLinha.objects.all().delete()
        
        # Remove rotas
        dados_removidos['Rotas'] = Rota.objects.count()
        Rota.objects.all().delete()
        
        if verbose:
            self.stdout.write('✅ Rotas removidas')
        
        return dados_removidos

    def _limpar_usuarios(self, verbose=False):
        """Remove dados de usuários"""
        if verbose:
            self.stdout.write('👤 Removendo usuários...')
        
        dados_removidos = {}
        
        # Remove usuários
        dados_removidos['Usuários'] = Usuario.objects.count()
        Usuario.objects.all().delete()
        
        if verbose:
            self.stdout.write('✅ Usuários removidos')
        
        return dados_removidos

    def _limpar_relacionamentos(self, verbose=False):
        """Remove apenas relacionamentos, mantendo paradas e linhas"""
        if verbose:
            self.stdout.write('🔗 Removendo relacionamentos...')
        
        dados_removidos = {}
        
        # Remove todos os relacionamentos
        dados_removidos['Relacionamentos Rota-Parada'] = RotaParada.objects.count()
        RotaParada.objects.all().delete()
        
        dados_removidos['Relacionamentos Rota-Linha'] = RotaLinha.objects.count()
        RotaLinha.objects.all().delete()
        
        dados_removidos['Relacionamentos Linha-Parada'] = LinhaParada.objects.count()
        LinhaParada.objects.all().delete()
        
        if verbose:
            self.stdout.write('✅ Relacionamentos removidos')
        
        return dados_removidos

    def _exibir_resultado_limpeza(self, dados_removidos):
        """Exibe resultado da limpeza"""
        if not dados_removidos:
            self.stdout.write('ℹ️  Nenhum dado foi removido')
            return
        
        self.stdout.write('\n📊 DADOS REMOVIDOS:')
        total_removido = 0
        
        for tipo, quantidade in dados_removidos.items():
            if quantidade > 0:
                self.stdout.write(f'  🗑️  {tipo}: {quantidade}')
                total_removido += quantidade
            else:
                self.stdout.write(f'  📊 {tipo}: {quantidade}')
        
        self.stdout.write(f'\n📈 Total de registros removidos: {total_removido}')
        
        # Exibe estatísticas atuais
        self.stdout.write('\n📊 ESTATÍSTICAS ATUAIS:')
        stats_atuais = {
            'Paradas': Parada.objects.count(),
            'Linhas': Linha.objects.count(),
            'Relacionamentos Linha-Parada': LinhaParada.objects.count(),
            'Rotas': Rota.objects.count(),
            'Relacionamentos Rota-Linha': RotaLinha.objects.count(),
            'Relacionamentos Rota-Parada': RotaParada.objects.count(),
            'Usuários': Usuario.objects.count(),
        }
        
        for item, count in stats_atuais.items():
            self.stdout.write(f'  📊 {item}: {count}')

    def _criar_backup(self, verbose=False):
        """Cria backup dos dados antes da limpeza (implementação futura)"""
        if verbose:
            self.stdout.write('💾 Funcionalidade de backup será implementada no futuro')
        
        # TODO: Implementar backup usando django-dbbackup ou similar
        pass 