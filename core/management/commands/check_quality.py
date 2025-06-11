"""
Comando Django para verificar a qualidade geral do código.

Este comando executa uma série de verificações automáticas para garantir
que o código está seguindo as melhores práticas e padrões de qualidade.

Verificações incluídas:
- Análise estática com flake8
- Verificação de segurança
- Cobertura de testes
- Performance de queries
- Conformidade com PEP8
- Documentação de código

Uso:
    python manage.py check_quality
    python manage.py check_quality --verbose
    python manage.py check_quality --fix-issues
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import connection
from django.core.cache import cache
import subprocess
import sys
import os


class Command(BaseCommand):
    """
    Comando para verificação de qualidade de código.
    
    Executa múltiplas verificações automáticas e gera relatório
    detalhado com sugestões de melhorias.
    """
    
    help = 'Verifica a qualidade geral do código do projeto BusFeed'
    
    def add_arguments(self, parser):
        """Adiciona argumentos opcionais ao comando."""
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Exibe output detalhado das verificações',
        )
        parser.add_argument(
            '--fix-issues',
            action='store_true',
            help='Tenta corrigir automaticamente problemas encontrados',
        )
        parser.add_argument(
            '--skip-tests',
            action='store_true',
            help='Pula a execução dos testes (mais rápido)',
        )
    
    def handle(self, *args, **options):
        """Executa todas as verificações de qualidade."""
        self.verbosity = options.get('verbosity', 1)
        self.verbose = options['verbose']
        self.fix_issues = options['fix_issues']
        self.skip_tests = options['skip_tests']
        
        self.stdout.write(
            self.style.SUCCESS('🔍 Iniciando verificação de qualidade do BusFeed...\n')
        )
        
        # Executar todas as verificações
        results = {
            'django_check': self.check_django_configuration(),
            'code_style': self.check_code_style(),
            'security': self.check_security(),
            'performance': self.check_performance(),
            'documentation': self.check_documentation(),
        }
        
        if not self.skip_tests:
            results['tests'] = self.check_tests()
        
        # Gerar relatório final
        self.generate_report(results)
    
    def check_django_configuration(self):
        """Verifica configurações do Django."""
        self.stdout.write('📋 Verificando configurações do Django...')
        
        issues = []
        
        try:
            # Executar django check
            result = subprocess.run(
                [sys.executable, 'manage.py', 'check', '--deploy'],
                capture_output=True,
                text=True,
                cwd=settings.BASE_DIR
            )
            
            if result.returncode == 0:
                self.stdout.write(self.style.SUCCESS('  ✅ Configurações OK'))
                return {'status': 'ok', 'issues': []}
            else:
                issues = result.stdout.split('\n')
                self.stdout.write(self.style.WARNING('  ⚠️  Problemas encontrados'))
                if self.verbose:
                    for issue in issues:
                        if issue.strip():
                            self.stdout.write(f'    {issue}')
                            
        except Exception as e:
            issues.append(f'Erro ao executar django check: {e}')
            self.stdout.write(self.style.ERROR('  ❌ Erro na verificação'))
        
        return {'status': 'warning' if issues else 'ok', 'issues': issues}
    
    def check_code_style(self):
        """Verifica estilo e formatação do código."""
        self.stdout.write('🎨 Verificando estilo do código...')
        
        issues = []
        
        # Verificar com flake8
        try:
            result = subprocess.run(
                ['flake8', '.', '--max-line-length=100', '--exclude=migrations'],
                capture_output=True,
                text=True,
                cwd=settings.BASE_DIR
            )
            
            if result.stdout:
                issues.extend(result.stdout.split('\n'))
                
        except FileNotFoundError:
            issues.append('flake8 não instalado. Execute: pip install flake8')
        except Exception as e:
            issues.append(f'Erro ao executar flake8: {e}')
        
        # Auto-fix com black se solicitado
        if self.fix_issues:
            try:
                subprocess.run(
                    ['black', '.', '--line-length=100'],
                    capture_output=True,
                    cwd=settings.BASE_DIR
                )
                self.stdout.write('  🔧 Formatação automática aplicada com black')
            except FileNotFoundError:
                self.stdout.write('  ⚠️  black não instalado para auto-fix')
        
        status = 'error' if len(issues) > 10 else 'warning' if issues else 'ok'
        
        if status == 'ok':
            self.stdout.write(self.style.SUCCESS('  ✅ Estilo de código OK'))
        else:
            self.stdout.write(self.style.WARNING(f'  ⚠️  {len(issues)} problemas de estilo'))
            if self.verbose and issues:
                for issue in issues[:5]:  # Mostrar apenas os primeiros 5
                    if issue.strip():
                        self.stdout.write(f'    {issue}')
        
        return {'status': status, 'issues': issues}
    
    def check_security(self):
        """Verifica problemas de segurança."""
        self.stdout.write('🔒 Verificando segurança...')
        
        issues = []
        
        # Verificações básicas de configuração
        if settings.DEBUG and not settings.ALLOWED_HOSTS:
            issues.append('ALLOWED_HOSTS vazio em modo DEBUG')
        
        if settings.SECRET_KEY == 'django-insecure-development-key-change-in-production':
            issues.append('SECRET_KEY usando valor padrão inseguro')
        
        # Verificar com bandit se disponível
        try:
            result = subprocess.run(
                ['bandit', '-r', '.', '-f', 'txt', '--skip', 'B101'],
                capture_output=True,
                text=True,
                cwd=settings.BASE_DIR
            )
            
            if 'No issues identified' not in result.stdout and result.stdout:
                security_issues = result.stdout.split('\n')[-10:]  # Últimas 10 linhas
                issues.extend(security_issues)
                
        except FileNotFoundError:
            issues.append('bandit não instalado. Execute: pip install bandit')
        except Exception as e:
            issues.append(f'Erro ao executar bandit: {e}')
        
        status = 'error' if len(issues) > 5 else 'warning' if issues else 'ok'
        
        if status == 'ok':
            self.stdout.write(self.style.SUCCESS('  ✅ Segurança OK'))
        else:
            self.stdout.write(self.style.WARNING(f'  ⚠️  {len(issues)} problemas de segurança'))
        
        return {'status': status, 'issues': issues}
    
    def check_performance(self):
        """Verifica performance e otimizações."""
        self.stdout.write('⚡ Verificando performance...')
        
        issues = []
        
        # Verificar configuração de cache
        if 'locmem' in settings.CACHES['default']['BACKEND']:
            issues.append('Cache local em produção pode impactar performance')
        
        # Verificar configuração de banco
        if 'sqlite3' in settings.DATABASES['default']['ENGINE'] and not settings.DEBUG:
            issues.append('SQLite em produção pode impactar performance')
        
        # Testar velocidade de conexão com banco
        try:
            import time
            start = time.time()
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            db_time = (time.time() - start) * 1000
            
            if db_time > 100:  # Mais de 100ms
                issues.append(f'Conexão com banco lenta: {db_time:.2f}ms')
        except Exception as e:
            issues.append(f'Erro ao testar conexão com banco: {e}')
        
        # Testar cache
        try:
            import time
            start = time.time()
            cache.set('test_key', 'test_value', 30)
            cache.get('test_key')
            cache_time = (time.time() - start) * 1000
            
            if cache_time > 50:  # Mais de 50ms
                issues.append(f'Cache lento: {cache_time:.2f}ms')
        except Exception as e:
            issues.append(f'Erro ao testar cache: {e}')
        
        status = 'warning' if issues else 'ok'
        
        if status == 'ok':
            self.stdout.write(self.style.SUCCESS('  ✅ Performance OK'))
        else:
            self.stdout.write(self.style.WARNING(f'  ⚠️  {len(issues)} problemas de performance'))
        
        return {'status': status, 'issues': issues}
    
    def check_tests(self):
        """Verifica cobertura e qualidade dos testes."""
        self.stdout.write('🧪 Verificando testes...')
        
        issues = []
        
        try:
            # Executar testes
            result = subprocess.run(
                [sys.executable, 'manage.py', 'test', '--verbosity=0'],
                capture_output=True,
                text=True,
                cwd=settings.BASE_DIR
            )
            
            if result.returncode != 0:
                issues.append('Alguns testes estão falhando')
                if self.verbose:
                    self.stdout.write(result.stdout)
            
            # Verificar cobertura se coverage estiver disponível
            try:
                subprocess.run(
                    ['coverage', 'run', '--source=.', 'manage.py', 'test'],
                    capture_output=True,
                    cwd=settings.BASE_DIR
                )
                
                result = subprocess.run(
                    ['coverage', 'report', '--show-missing'],
                    capture_output=True,
                    text=True,
                    cwd=settings.BASE_DIR
                )
                
                # Extrair porcentagem de cobertura
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'TOTAL' in line:
                        parts = line.split()
                        if len(parts) > 3 and '%' in parts[3]:
                            coverage_pct = int(parts[3].replace('%', ''))
                            if coverage_pct < 80:
                                issues.append(f'Cobertura de testes baixa: {coverage_pct}%')
                            break
                        
            except FileNotFoundError:
                issues.append('coverage não instalado. Execute: pip install coverage')
                
        except Exception as e:
            issues.append(f'Erro ao executar testes: {e}')
        
        status = 'error' if any('falhando' in issue for issue in issues) else 'warning' if issues else 'ok'
        
        if status == 'ok':
            self.stdout.write(self.style.SUCCESS('  ✅ Testes OK'))
        else:
            self.stdout.write(self.style.WARNING(f'  ⚠️  {len(issues)} problemas nos testes'))
        
        return {'status': status, 'issues': issues}
    
    def check_documentation(self):
        """Verifica documentação do código."""
        self.stdout.write('📚 Verificando documentação...')
        
        issues = []
        
        # Verificar se arquivos essenciais existem
        essential_docs = ['README.md', 'MELHORIAS_ACESSIBILIDADE.md']
        for doc in essential_docs:
            if not os.path.exists(os.path.join(settings.BASE_DIR, doc)):
                issues.append(f'Documentação faltando: {doc}')
        
        # TODO: Verificar docstrings em funções e classes
        # Isso poderia ser implementado com ast para analisar o código
        
        status = 'warning' if issues else 'ok'
        
        if status == 'ok':
            self.stdout.write(self.style.SUCCESS('  ✅ Documentação OK'))
        else:
            self.stdout.write(self.style.WARNING(f'  ⚠️  {len(issues)} problemas de documentação'))
        
        return {'status': status, 'issues': issues}
    
    def generate_report(self, results):
        """Gera relatório final da verificação."""
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('📊 RELATÓRIO DE QUALIDADE DO CÓDIGO'))
        self.stdout.write('='*60)
        
        # Contadores
        total_issues = sum(len(result['issues']) for result in results.values())
        passed_checks = sum(1 for result in results.values() if result['status'] == 'ok')
        total_checks = len(results)
        
        # Status geral
        if total_issues == 0:
            overall_status = self.style.SUCCESS('✅ EXCELENTE')
        elif total_issues < 10:
            overall_status = self.style.WARNING('⚠️  BOM (com melhorias)')
        else:
            overall_status = self.style.ERROR('❌ PRECISA MELHORAR')
        
        self.stdout.write(f'\nStatus Geral: {overall_status}')
        self.stdout.write(f'Verificações Passaram: {passed_checks}/{total_checks}')
        self.stdout.write(f'Total de Problemas: {total_issues}')
        
        # Resumo por categoria
        self.stdout.write('\n📋 Resumo por Categoria:')
        for category, result in results.items():
            status_icon = {
                'ok': '✅',
                'warning': '⚠️ ',
                'error': '❌'
            }.get(result['status'], '❓')
            
            self.stdout.write(f'  {status_icon} {category.replace("_", " ").title()}: '
                            f'{len(result["issues"])} problemas')
        
        # Recomendações
        if total_issues > 0:
            self.stdout.write('\n💡 Recomendações:')
            
            if results.get('code_style', {}).get('issues'):
                self.stdout.write('  • Execute: black . --line-length=100 (formatação)')
                self.stdout.write('  • Execute: flake8 . (verificar estilo)')
            
            if results.get('security', {}).get('issues'):
                self.stdout.write('  • Revise configurações de segurança')
                self.stdout.write('  • Execute: bandit -r . (análise de segurança)')
            
            if results.get('tests', {}).get('issues'):
                self.stdout.write('  • Aumente cobertura de testes (meta: >80%)')
                self.stdout.write('  • Execute: coverage run --source=. manage.py test')
            
            if results.get('performance', {}).get('issues'):
                self.stdout.write('  • Configure Redis para cache em produção')
                self.stdout.write('  • Use PostgreSQL em produção')
        
        # Score final
        score = max(0, 100 - (total_issues * 5))
        score_color = (
            self.style.SUCCESS if score >= 90 else
            self.style.WARNING if score >= 70 else
            self.style.ERROR
        )
        
        self.stdout.write(f'\n🎯 Score de Qualidade: {score_color(f"{score}/100")}')
        
        if score >= 90:
            self.stdout.write(self.style.SUCCESS('🏆 Parabéns! Código de alta qualidade!'))
        elif score >= 70:
            self.stdout.write(self.style.WARNING('📈 Bom código, mas há espaço para melhorias'))
        else:
            self.stdout.write(self.style.ERROR('🔧 Código precisa de atenção urgente'))
        
        self.stdout.write('\n' + '='*60 + '\n') 