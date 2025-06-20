# 🚌 BusFeed - Sistema de Transporte Público do DF

## 📋 Sobre o Projeto

O **BusFeed** é um sistema web moderno desenvolvido para otimizar o transporte público do Distrito Federal, criado em parceria com a **Secretaria de Transporte e Mobilidade (SEMOB-DF)** e **DFTrans**.

### 🎯 Objetivo Principal
Fornecer aos cidadãos do DF uma plataforma intuitiva e eficiente para:
- Consultar rotas de ônibus em tempo real
- Localizar paradas próximas
- Planejar viagens de transporte público
- Acessar informações sobre linhas e horários

---

## 🏗️ Arquitetura do Sistema

### 📐 Padrão Arquitetural
- **Backend**: Django MVC com apps modulares orientados a domínio
- **Frontend**: React SPA com componentes reutilizáveis
- **Banco de Dados**: PostgreSQL com extensão PostGIS para dados geográficos
- **Containerização**: Docker e Docker Compose

### 🔧 Apps Django (Domínios Funcionais)

#### 1. **`paradas/`** - Gerenciamento de Paradas
```python
# models.py - Exemplo de estrutura
class Parada(models.Model):
    nome = models.CharField(max_length=200)
    codigo_dftrans = models.CharField(max_length=50, unique=True)
    localizacao = models.PointField()  # PostGIS
    tem_acessibilidade = models.BooleanField(default=False)
    tipo = models.CharField(choices=TIPOS_PARADA)
```

**Funcionalidades**:
- ✅ CRUD completo de paradas
- ✅ Busca geográfica com PostGIS
- ✅ API para autocomplete
- ✅ Filtros por acessibilidade e tipo

#### 2. **`linhas/`** - Linhas de Ônibus
```python
# models.py
class Linha(models.Model):
    numero = models.CharField(max_length=20)
    nome = models.CharField(max_length=200)
    origem = models.CharField(max_length=200)
    destino = models.CharField(max_length=200)
    operadora = models.CharField(max_length=100)
    valor_passagem = models.DecimalField(max_digits=5, decimal_places=2)
```

**Funcionalidades**:
- ✅ Gestão de linhas e itinerários
- ✅ Integração com DFTrans API
- ✅ Sincronização automática de dados
- ✅ Monitoramento em tempo real

#### 3. **`rotas/`** - Cálculo de Rotas
```python
# services.py
class CalculadoraRotas:
    def calcular_melhor_rota(self, origem, destino):
        """
        Calcula a melhor rota entre dois pontos
        considerando tempo, distância e baldeações
        """
        pass
```

**Funcionalidades**:
- ✅ Algoritmo de cálculo de rotas
- ✅ Otimização por tempo/distância
- ✅ Sugestão de baldeações
- ✅ Integração com mapas

#### 4. **`usuarios/`** - Gestão de Usuários
```python
# models.py
class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    paradas_favoritas = models.ManyToManyField('paradas.Parada')
    linhas_favoritas = models.ManyToManyField('linhas.Linha')
```

**Funcionalidades**:
- ✅ Sistema de autenticação
- ✅ Perfis personalizados
- ✅ Favoritos e preferências
- ✅ Histórico de buscas

---

## 🛠️ Stack Tecnológica

### Backend (Django)
```txt
# requirements.txt
Django==4.2.7
djangorestframework==3.14.0
django-cors-headers==4.3.1
psycopg2-binary==2.9.7
django-environ==0.11.2
celery==5.3.4
redis==5.0.1
requests==2.31.0
geopy==2.4.0
```

**Justificativas das Escolhas**:
- **Django**: Framework robusto com ORM poderoso e admin interface
- **DRF**: APIs REST padronizadas e documentação automática
- **PostgreSQL + PostGIS**: Suporte nativo a dados geográficos
- **Celery + Redis**: Processamento assíncrono para tarefas pesadas
- **Docker**: Ambiente consistente entre desenvolvimento e produção

### Frontend (React)
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-router-dom": "^6.8.0",
    "bootstrap": "^5.3.0",
    "react-bootstrap": "^2.9.0",
    "leaflet": "^1.9.4",
    "react-leaflet": "^4.2.1",
    "axios": "^1.6.0"
  }
}
```

**Justificativas das Escolhas**:
- **React**: Componentes reutilizáveis e estado reativo
- **Bootstrap**: Design system consistente e responsivo
- **Leaflet**: Mapas interativos leves e personalizáveis
- **Axios**: Cliente HTTP com interceptors e tratamento de erros

---

## 🎨 Componentes Frontend

### 📱 Estrutura de Páginas
```
src/
├── pages/
│   ├── Home.js              # Página inicial com busca
│   ├── MapPage.js           # Mapa interativo
│   ├── ParadasPage.js       # Lista de paradas (INTERATIVA)
│   ├── LinhasPage.js        # Catálogo de linhas
│   └── RouteResultsPage.js  # Resultados de rotas
├── components/
│   ├── common/              # Componentes reutilizáveis
│   │   ├── Header.js        # Cabeçalho com navegação
│   │   ├── SearchForm.js    # Formulário de busca
│   │   └── RouteResult.js   # Card de resultado
│   └── map/                 # Componentes de mapa
│       ├── MapView.js       # Componente principal do mapa
│       └── RouteDetails.js  # Detalhes de rota
└── services/
    ├── api.js               # Cliente HTTP configurado
    └── routeService.js      # Lógica de rotas
```

### 🎯 Página Interativa - ParadasPage.js

A página de paradas foi completamente reformulada com funcionalidades interativas:

#### **Estados Gerenciados**
```javascript
// Estados de filtros e busca
const [searchTerm, setSearchTerm] = useState('');
const [filterType, setFilterType] = useState('all');
const [filterAccessibility, setFilterAccessibility] = useState('all');
const [sortBy, setSortBy] = useState('name');

// Estados para interatividade (removidos na versão atual)
// Implementação focou em hover effects e animações CSS
```

#### **Funcionalidades Implementadas**
1. **🔍 Sistema de Filtros Avançado**
   - Busca por nome/descrição
   - Filtro por tipo (Principal/Secundária)
   - Filtro por acessibilidade
   - Ordenação por nome, movimento ou número de linhas

2. **🎨 Animações e Micro-interações**
   - Hover effects com elevação dos cards
   - Transições suaves em todos os elementos
   - Feedback visual imediato
   - Design responsivo para mobile

3. **📊 Visualização de Dados**
   - Cards informativos com estatísticas
   - Badges coloridos para linhas
   - Indicadores de acessibilidade
   - Layout em grid responsivo

#### **Código de Exemplo - Card Interativo**
```javascript
<Card 
  className={`h-100 stop-card ${getStopTypeClass(stop.type)}`}
  style={{
    background: 'var(--color-white)',
    borderRadius: '16px',
    border: 'none',
    boxShadow: '0 4px 16px rgba(0,0,0,0.08)',
    transition: 'all 0.3s ease',
    cursor: 'pointer'
  }}
  onMouseEnter={(e) => {
    e.currentTarget.style.transform = 'translateY(-4px)';
    e.currentTarget.style.boxShadow = '0 8px 24px rgba(0,0,0,0.15)';
  }}
  onMouseLeave={(e) => {
    e.currentTarget.style.transform = 'translateY(0)';
    e.currentTarget.style.boxShadow = '0 4px 16px rgba(0,0,0,0.08)';
  }}
>
```

---

## 🗄️ Modelagem de Dados

### 🔗 Relacionamentos Principais
```python
# Relacionamento Many-to-Many entre Linhas e Paradas
class LinhaParada(models.Model):
    linha = models.ForeignKey('Linha', on_delete=models.CASCADE)
    parada = models.ForeignKey('Parada', on_delete=models.CASCADE)
    ordem = models.PositiveIntegerField()  # Sequência na rota
    tempo_estimado = models.DurationField(null=True, blank=True)
    
    class Meta:
        unique_together = ['linha', 'parada', 'ordem']
        ordering = ['ordem']
```

### 📍 Dados Geográficos (PostGIS)
```python
# Consulta de paradas próximas
def paradas_proximas(latitude, longitude, raio_metros=1000):
    ponto_usuario = Point(longitude, latitude, srid=4326)
    return Parada.objects.filter(
        localizacao__distance_lte=(ponto_usuario, D(m=raio_metros))
    ).annotate(
        distancia=Distance('localizacao', ponto_usuario)
    ).order_by('distancia')
```

---

## 🚀 APIs e Integração

### 🔌 Endpoints Principais
```python
# urls.py - Estrutura de URLs
urlpatterns = [
    # APIs de Paradas
    path('api/paradas/', include('paradas.urls')),
    path('api/paradas/proximas/', ParadasProximasView.as_view()),
    path('api/paradas/autocomplete/', AutocompleteParadasView.as_view()),
    
    # APIs de Linhas
    path('api/linhas/', include('linhas.urls')),
    path('api/linhas/<str:numero>/', DetalheLinha.as_view()),
    
    # APIs de Rotas
    path('api/rotas/calcular/', CalcularRotaView.as_view()),
    path('api/rotas/otimizar/', OtimizarRotaView.as_view()),
]
```

### 📡 Integração DFTrans
```python
# services/dftrans_api.py
class DFTransAPI:
    BASE_URL = "https://api.dftrans.df.gov.br"
    
    def sincronizar_linhas(self):
        """Sincroniza dados das linhas com DFTrans"""
        response = requests.get(f"{self.BASE_URL}/linhas")
        for linha_data in response.json():
            self._criar_ou_atualizar_linha(linha_data)
    
    def obter_tempo_real(self, linha_numero):
        """Obtém posição dos ônibus em tempo real"""
        return requests.get(f"{self.BASE_URL}/tempo-real/{linha_numero}")
```

---

## 🐳 Containerização e Deploy

### 🔧 Docker Configuration
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gdal-bin \
    libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

### 🚀 Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  db:
    image: postgis/postgis:15-3.3
    environment:
      POSTGRES_DB: busfeed
      POSTGRES_USER: busfeed_user
      POSTGRES_PASSWORD: busfeed_pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      - DATABASE_URL=postgis://busfeed_user:busfeed_pass@db:5432/busfeed

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
    environment:
      - REACT_APP_API_URL=http://localhost:8000
```

---

## 📊 Funcionalidades por Módulo

### 🚏 Módulo Paradas
- [x] **CRUD Completo**: Criar, ler, atualizar, deletar paradas
- [x] **Busca Geográfica**: Encontrar paradas próximas usando PostGIS
- [x] **Filtros Avançados**: Por tipo, acessibilidade, linhas
- [x] **API REST**: Endpoints documentados com DRF
- [x] **Interface Interativa**: Cards com hover effects e animações

### 🚌 Módulo Linhas
- [x] **Gestão de Linhas**: Cadastro e manutenção de rotas
- [x] **Integração DFTrans**: Sincronização automática de dados
- [x] **Monitoramento**: Commands para atualização periódica
- [x] **Relacionamentos**: Ligação com paradas via LinhaParada

### 🗺️ Módulo Rotas
- [x] **Cálculo de Rotas**: Algoritmo para encontrar melhores caminhos
- [x] **Otimização**: Por tempo, distância ou número de baldeações
- [x] **Visualização**: Integração com mapas Leaflet
- [x] **Resultados Detalhados**: Informações completas da viagem

### 👤 Módulo Usuários
- [x] **Autenticação**: Sistema de login/registro
- [x] **Perfis**: Personalização de preferências
- [x] **Favoritos**: Paradas e linhas favoritas
- [x] **Histórico**: Registro de buscas realizadas

---

## 🧪 Testes e Qualidade

### 🔍 Estrutura de Testes
```python
# paradas/tests.py
class ParadaModelTest(TestCase):
    def test_criacao_parada(self):
        """Testa criação de parada com dados válidos"""
        parada = Parada.objects.create(
            nome="Terminal Ceilândia",
            codigo_dftrans="TERM001",
            localizacao=Point(-48.1089, -15.8267)
        )
        self.assertEqual(parada.nome, "Terminal Ceilândia")

class ParadaAPITest(APITestCase):
    def test_busca_paradas_proximas(self):
        """Testa endpoint de paradas próximas"""
        response = self.client.get('/api/paradas/proximas/', {
            'latitude': -15.8267,
            'longitude': -48.1089,
            'raio': 1000
        })
        self.assertEqual(response.status_code, 200)
```

### 📈 Comandos de Gerenciamento
```python
# management/commands/sincronizar_dftrans.py
class Command(BaseCommand):
    help = 'Sincroniza dados com DFTrans API'
    
    def handle(self, *args, **options):
        dftrans = DFTransAPI()
        dftrans.sincronizar_linhas()
        self.stdout.write(
            self.style.SUCCESS('Sincronização concluída com sucesso!')
        )
```

---

## 🚀 Como Executar o Projeto

### 🔧 Pré-requisitos
- Python 3.11+
- Node.js 18+
- Docker e Docker Compose
- PostgreSQL com PostGIS (ou usar container)

### 📦 Instalação Local

1. **Clone o repositório**
```bash
git clone <repository-url>
cd ProjetoPt2
```

2. **Configure o ambiente**
```bash
# Backend
cp env.example .env
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

3. **Execute com Docker**
```bash
docker-compose up -d
```

4. **Acesse a aplicação**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Admin Django: http://localhost:8000/admin

### 🗄️ Comandos Úteis
```bash
# Executar migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Sincronizar dados DFTrans
python manage.py sincronizar_dftrans

# Executar testes
python manage.py test

# Coletar arquivos estáticos
python manage.py collectstatic
```

---

## 📝 Próximos Passos

### 🔮 Roadmap de Desenvolvimento
1. **Fase 3**: Sistema de notificações push
2. **Fase 4**: App mobile React Native
3. **Fase 5**: IA para previsão de atrasos
4. **Fase 6**: Integração com sistemas de pagamento

### 🐛 Melhorias Identificadas
- [ ] Cache Redis para consultas frequentes
- [ ] Testes de carga e performance
- [ ] Monitoramento com Sentry
- [ ] CI/CD com GitHub Actions
- [ ] Documentação API com Swagger

---

## 👥 Equipe de Desenvolvimento

**Projeto Acadêmico - Análise e Desenvolvimento de Sistemas**
- Desenvolvimento Full Stack
- Integração com APIs governamentais
- Foco em UX/UI e acessibilidade

---

## 📄 Licença

Este projeto foi desenvolvido para fins acadêmicos em parceria com órgãos públicos do Distrito Federal.

---

## 📞 Suporte

Para dúvidas sobre o projeto:
- 📧 Email: suporte@busfeed.df.gov.br
- 📱 WhatsApp: (61) 9999-9999
- 🌐 Site: https://busfeed.df.gov.br

---

*Última atualização: Dezembro 2024* 