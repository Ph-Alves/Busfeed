"""
Comando de migração para transferir dados geográficos existentes
para os novos campos PostGIS.
"""

from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from django.db import transaction
from paradas.models import Parada
from linhas.models import Linha
from rotas.models import Rota
import os


class Command(BaseCommand):
    help = 'Migra dados geográficos existentes para campos PostGIS'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Executa sem salvar alterações (modo teste)',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Tamanho do lote para processamento',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        batch_size = options['batch_size']
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('MODO DRY-RUN: Nenhuma alteração será salva.')
            )

        self.stdout.write('Iniciando migração para PostGIS...')
        
        # Migrar paradas
        self.migrar_paradas(batch_size, dry_run)
        
        # Migrar rotas
        self.migrar_rotas(batch_size, dry_run)
        
        # Gerar geometrias de trajetos das linhas
        self.gerar_trajetos_linhas(dry_run)
        
        self.stdout.write(
            self.style.SUCCESS('Migração concluída com sucesso!')
        )

    def migrar_paradas(self, batch_size, dry_run):
        """Migra coordenadas das paradas para campos PostGIS"""
        self.stdout.write('Migrando paradas...')
        
        paradas_sem_localizacao = Parada.objects.filter(localizacao__isnull=True)
        total = paradas_sem_localizacao.count()
        
        if total == 0:
            self.stdout.write('  Nenhuma parada para migrar.')
            return
        
        self.stdout.write(f'  Encontradas {total} paradas para migrar.')
        
        migradas = 0
        with transaction.atomic():
            for parada in paradas_sem_localizacao.iterator(chunk_size=batch_size):
                if hasattr(parada, 'latitude') and hasattr(parada, 'longitude'):
                    try:
                        # Cria o ponto geográfico
                        parada.localizacao = Point(
                            parada.longitude, 
                            parada.latitude, 
                            srid=4326
                        )
                        
                        if not dry_run:
                            parada.save()
                        
                        migradas += 1
                        
                        if migradas % batch_size == 0:
                            self.stdout.write(f'  Migradas {migradas}/{total} paradas...')
                    
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f'  Erro ao migrar parada {parada.id}: {e}'
                            )
                        )
        
        self.stdout.write(f'  ✓ {migradas} paradas migradas com sucesso.')

    def migrar_rotas(self, batch_size, dry_run):
        """Migra coordenadas das rotas para campos PostGIS"""
        self.stdout.write('Migrando rotas...')
        
        rotas_sem_pontos = Rota.objects.filter(origem_ponto__isnull=True)
        total = rotas_sem_pontos.count()
        
        if total == 0:
            self.stdout.write('  Nenhuma rota para migrar.')
            return
        
        self.stdout.write(f'  Encontradas {total} rotas para migrar.')
        
        migradas = 0
        with transaction.atomic():
            for rota in rotas_sem_pontos.iterator(chunk_size=batch_size):
                try:
                    # Cria os pontos de origem e destino
                    rota.origem_ponto = Point(
                        rota.origem_longitude, 
                        rota.origem_latitude, 
                        srid=4326
                    )
                    rota.destino_ponto = Point(
                        rota.destino_longitude, 
                        rota.destino_latitude, 
                        srid=4326
                    )
                    
                    if not dry_run:
                        rota.save()
                    
                    migradas += 1
                    
                    if migradas % batch_size == 0:
                        self.stdout.write(f'  Migradas {migradas}/{total} rotas...')
                
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'  Erro ao migrar rota {rota.id}: {e}'
                        )
                    )
        
        self.stdout.write(f'  ✓ {migradas} rotas migradas com sucesso.')

    def gerar_trajetos_linhas(self, dry_run):
        """Gera geometrias de trajetos para as linhas baseadas nas paradas"""
        self.stdout.write('Gerando trajetos das linhas...')
        
        linhas = Linha.objects.all()
        total = linhas.count()
        
        if total == 0:
            self.stdout.write('  Nenhuma linha encontrada.')
            return
        
        geradas = 0
        for linha in linhas:
            try:
                if not dry_run:
                    trajeto = linha.gerar_trajeto_das_paradas()
                    if trajeto:
                        geradas += 1
                else:
                    # Verifica se seria possível gerar
                    paradas = linha.get_paradas_ordenadas()
                    if paradas.count() >= 2:
                        geradas += 1
            
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'  Erro ao gerar trajeto da linha {linha.codigo}: {e}'
                    )
                )
        
        self.stdout.write(f'  ✓ {geradas} trajetos de linhas gerados.')

    def verificar_integridade(self):
        """Verifica a integridade dos dados migrados"""
        self.stdout.write('Verificando integridade dos dados...')
        
        # Paradas com coordenadas mas sem localização PostGIS
        paradas_inconsistentes = Parada.objects.filter(
            latitude__isnull=False,
            longitude__isnull=False,
            localizacao__isnull=True
        ).count()
        
        if paradas_inconsistentes > 0:
            self.stdout.write(
                self.style.WARNING(
                    f'  ⚠ {paradas_inconsistentes} paradas com dados inconsistentes.'
                )
            )
        
        # Rotas com coordenadas mas sem pontos PostGIS
        rotas_inconsistentes = Rota.objects.filter(
            origem_latitude__isnull=False,
            origem_longitude__isnull=False,
            origem_ponto__isnull=True
        ).count()
        
        if rotas_inconsistentes > 0:
            self.stdout.write(
                self.style.WARNING(
                    f'  ⚠ {rotas_inconsistentes} rotas com dados inconsistentes.'
                )
            )
        
        if paradas_inconsistentes == 0 and rotas_inconsistentes == 0:
            self.stdout.write('  ✓ Dados íntegros.') 