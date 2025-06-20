# 🎥 Roteiro Vídeo - BusFeed Parte 2

## 📋 Informações Gerais
- **Duração Total**: 10 minutos
- **Projeto**: BusFeed - Sistema de Transporte Público do DF
- **Fase**: Parte 2 - Desenvolvimento Full Stack
- **Grupo**: [Seu Nome/Grupo]

---

## ⏱️ 0:00 – 0:30 | 1. Abertura

### 🎬 **Slide de Abertura**
```
🚌 BUSFEED
Sistema de Transporte Público do Distrito Federal

PARTE 2 - DESENVOLVIMENTO FULL STACK

Secretarias Envolvidas:
• SEMOB-DF (Secretaria de Transporte e Mobilidade)
• DFTrans (Transporte Urbano do DF)

Desenvolvido por: [Seu Nome]
Curso: Análise e Desenvolvimento de Sistemas
```

### 🎤 **Narração**
> "Olá! Bem-vindos à apresentação da Parte 2 do projeto BusFeed, um sistema web completo para otimização do transporte público do Distrito Federal. Nesta fase, desenvolvemos uma solução full stack integrando Django no backend e React no frontend, em parceria com a SEMOB-DF e DFTrans."

---

## ⏱️ 0:30 – 1:30 | 2. Contextualização

### 📊 **Slide - Problema Identificado**
```
🚨 DESAFIOS DO TRANSPORTE PÚBLICO NO DF

• 2,8 milhões de habitantes na região metropolitana
• 1,2 milhão de viagens diárias no transporte público
• Falta de informações em tempo real para usuários
• Dificuldade em planejar rotas eficientes
• Baixa integração entre sistemas existentes

SOLUÇÃO: Sistema web unificado e acessível
```

### 🎤 **Narração**
> "O transporte público do DF atende milhões de usuários diariamente, mas enfrenta desafios significativos. A falta de informações centralizadas e em tempo real dificulta o planejamento de viagens. Identificamos a necessidade de uma plataforma unificada que conecte usuários, paradas, linhas e rotas de forma inteligente e acessível."

---

## ⏱️ 1:30 – 2:30 | 3. Objetivos e Escopo

### 🎯 **Slide - Objetivos da Parte 2**
```
🎯 OBJETIVOS DESTA FASE

OBJETIVO GERAL:
Desenvolver sistema web completo com backend Django e frontend React

OBJETIVOS ESPECÍFICOS:
✅ Implementar arquitetura modular orientada a domínios
✅ Criar APIs REST para integração de dados
✅ Desenvolver interface interativa e responsiva
✅ Integrar dados geográficos com PostGIS
✅ Estabelecer comunicação com APIs da DFTrans
```

### 🎤 **Narração**
> "Para esta fase, estabelecemos como objetivo principal criar um sistema web completo e funcional. Implementamos uma arquitetura robusta com Django no backend, oferecendo APIs REST documentadas, e React no frontend, proporcionando uma experiência de usuário moderna e interativa. O foco foi na modularidade e escalabilidade."

---

## ⏱️ 2:30 – 3:30 | 4. Levantamento de Requisitos

### 📋 **Slide - Requisitos Funcionais**
```
📋 REQUISITOS FUNCIONAIS

RF01 - Gerenciar paradas de ônibus
RF02 - Cadastrar e manter linhas de transporte
RF03 - Calcular rotas otimizadas
RF04 - Exibir mapa interativo com paradas
RF05 - Buscar paradas próximas (geolocalização)
RF06 - Filtrar e ordenar informações
RF07 - Sincronizar dados com DFTrans
RF08 - Autenticar usuários
RF09 - Gerenciar favoritos
RF10 - Compartilhar informações
```

### 📊 **Slide - Requisitos Não-Funcionais**
```
⚡ REQUISITOS NÃO-FUNCIONAIS

RNF01 - Performance: Respostas < 2 segundos
RNF02 - Segurança: Autenticação JWT
RNF03 - Usabilidade: Interface responsiva
RNF04 - Escalabilidade: Arquitetura modular
RNF05 - Disponibilidade: 99% uptime
RNF06 - Compatibilidade: Browsers modernos
RNF07 - Acessibilidade: WCAG 2.1 AA
RNF08 - Manutenibilidade: Código documentado
```

### 🎤 **Narração**
> "Realizamos um levantamento detalhado de requisitos junto aos stakeholders. Os requisitos funcionais cobrem desde o gerenciamento básico de paradas e linhas até funcionalidades avançadas como cálculo de rotas e sincronização em tempo real. Os requisitos não-funcionais garantem que o sistema seja performático, seguro e acessível."

---

## ⏱️ 3:30 – 4:30 | 5. Arquitetura & Modelagem

### 🏗️ **Slide - Arquitetura Geral**
```
🏗️ ARQUITETURA DO SISTEMA

┌─────────────────┐    ┌─────────────────┐
│   FRONTEND      │    │    BACKEND      │
│   React SPA     │◄──►│   Django REST   │
│   • Bootstrap   │    │   • PostgreSQL  │
│   • Leaflet.js  │    │   • PostGIS     │
│   • Axios       │    │   • Redis Cache │
└─────────────────┘    └─────────────────┘
         │                       │
         └───────────────────────┘
                    │
         ┌─────────────────┐
         │   INTEGRAÇÕES   │
         │   • DFTrans API │
         │   • OpenStreetMap│
         └─────────────────┘
```

### 📐 **Slide - Apps por Domínio**
```
🔧 MÓDULOS DO SISTEMA (Django Apps)

paradas/     🚏 Gerenciamento de Paradas
├── models.py      # Modelo de dados com PostGIS
├── views.py       # Views e ViewSets DRF
├── serializers.py # Serialização de dados
└── management/    # Comandos customizados

linhas/      🚌 Linhas de Ônibus
rotas/       🗺️ Cálculo de Rotas
usuarios/    👤 Autenticação e Perfis
services/    🔗 Integrações Externas
```

### 🎤 **Narração**
> "Adotamos uma arquitetura modular baseada em domínios funcionais. Cada app Django representa um domínio específico do negócio, promovendo baixo acoplamento e alta coesão. O frontend React consome APIs REST documentadas, garantindo separação clara entre apresentação e lógica de negócio."

---

## ⏱️ 4:30 – 6:30 | 6. Tecnologias e Bibliotecas

### 🛠️ **Slide - Stack Backend**
```
🐍 BACKEND - DJANGO STACK

Django 4.2+              Framework web robusto
Django REST Framework    APIs REST padronizadas
PostgreSQL + PostGIS     Banco com dados geográficos
Redis                    Cache e sessões
Celery                   Processamento assíncrono
Docker                   Containerização
Gunicorn                 Servidor WSGI
Nginx                    Proxy reverso
```

### ⚛️ **Slide - Stack Frontend**
```
⚛️ FRONTEND - REACT STACK

React 18+                Biblioteca de componentes
React Router            Roteamento SPA
Bootstrap 5             Framework CSS
React Bootstrap         Componentes Bootstrap
Leaflet.js              Mapas interativos
Axios                   Cliente HTTP
```

### 🎤 **Narração**
> "Escolhemos tecnologias consolidadas e bem documentadas. Django oferece um framework completo com ORM poderoso e admin interface. O PostgreSQL com PostGIS é essencial para operações geográficas. No frontend, React proporciona componentização e reatividade, enquanto Bootstrap garante responsividade e acessibilidade."

### 💡 **Slide - Justificativas Técnicas**
```
💡 JUSTIFICATIVAS DAS ESCOLHAS

Django + DRF
✓ Desenvolvimento rápido e seguro
✓ ORM com suporte a dados geográficos
✓ Admin interface para gestão
✓ Documentação automática de APIs

React + Bootstrap
✓ Componentes reutilizáveis
✓ Virtual DOM para performance
✓ Ecossistema maduro
✓ Design responsivo nativo

PostgreSQL + PostGIS
✓ Operações geográficas nativas
✓ Performance em consultas espaciais
✓ Padrão da indústria para GIS
```

---

## ⏱️ 6:30 – 8:30 | 7. Demonstração do Sistema

### 🖥️ **Gravação de Tela - Roteiro Detalhado**

#### **Tela 1: Página Inicial (30 segundos)**
🎤 *"Vamos iniciar a demonstração pela página inicial do BusFeed..."*

**Ações na tela:**
1. Abrir `http://localhost:3000`
2. Mostrar o header com navegação
3. Destacar o formulário de busca
4. Navegar pelos links do menu

#### **Tela 2: Página de Paradas Interativas (60 segundos)**
🎤 *"Esta é a funcionalidade principal que desenvolvemos - a página de paradas totalmente interativa..."*

**Ações na tela:**
1. Navegar para `/paradas`
2. Demonstrar filtros de busca:
   - Digitar "Terminal" na busca
   - Filtrar por tipo "Principal"
   - Filtrar por acessibilidade
3. Mostrar hover effects nos cards
4. Demonstrar responsividade (redimensionar janela)

#### **Tela 3: Mapa Interativo (45 segundos)**
🎤 *"O sistema inclui um mapa totalmente funcional com dados reais de Ceilândia..."*

**Ações na tela:**
1. Navegar para `/mapa`
2. Fazer zoom no mapa
3. Clicar em marcadores de paradas
4. Mostrar popups informativos
5. Navegar pelo mapa

#### **Tela 4: Backend Admin (30 segundos)**
🎤 *"No backend, temos uma interface administrativa completa para gestão de dados..."*

**Ações na tela:**
1. Abrir `http://localhost:8000/admin`
2. Fazer login
3. Mostrar listagem de paradas
4. Abrir uma parada para edição
5. Mostrar campos geográficos

#### **Tela 5: API Documentation (15 segundos)**
🎤 *"Todas as APIs são documentadas automaticamente..."*

**Ações na tela:**
1. Abrir `http://localhost:8000/api/docs/`
2. Mostrar interface Swagger
3. Expandir alguns endpoints

### 🎤 **Narração Contínua**
> "Como podem ver, o sistema está completamente funcional. A página de paradas oferece uma experiência rica com filtros avançados, animações suaves e design responsivo. O mapa integra dados reais de geolocalização, permitindo aos usuários visualizar paradas próximas. O backend fornece uma interface administrativa robusta e APIs bem documentadas."

---

## ⏱️ 8:30 – 9:30 | 8. Desafios e Aprendizados

### 🚧 **Slide - Principais Desafios**
```
🚧 DESAFIOS ENFRENTADOS

TÉCNICOS:
• Configuração do PostGIS em ambiente Docker
• Integração entre Django e React
• Otimização de consultas geográficas
• Gerenciamento de estado no frontend

ARQUITETURAIS:
• Definição de responsabilidades entre apps
• Estruturação de APIs RESTful
• Organização de componentes React

DADOS:
• Modelagem de relacionamentos complexos
• Sincronização com APIs externas
• Tratamento de dados geográficos
```

### 💡 **Slide - Soluções e Aprendizados**
```
💡 SOLUÇÕES IMPLEMENTADAS

✅ Docker Compose para ambiente consistente
✅ CORS configurado para comunicação frontend-backend
✅ Índices espaciais para performance em consultas GIS
✅ Hooks customizados para gerenciamento de estado
✅ Serializers DRF para transformação de dados
✅ Commands Django para automação de tarefas
✅ Componentização para reutilização de código

PRINCIPAIS APRENDIZADOS:
• Importância da documentação técnica
• Valor da arquitetura modular
• Benefícios do desenvolvimento orientado a testes
```

### 🎤 **Narração**
> "Durante o desenvolvimento, enfrentamos diversos desafios técnicos que se tornaram oportunidades de aprendizado. A configuração do ambiente com PostGIS exigiu conhecimento específico de containerização. A integração frontend-backend nos ensinou sobre CORS e autenticação. Cada obstáculo superado fortaleceu nossa compreensão das tecnologias envolvidas."

---

## ⏱️ 9:30 – 9:50 | 9. Próximos Passos

### 🔮 **Slide - Roadmap de Desenvolvimento**
```
🔮 PRÓXIMAS FASES DO PROJETO

FASE 3 - FUNCIONALIDADES AVANÇADAS
• Sistema de notificações push
• Integração completa com DFTrans API
• Algoritmos de otimização de rotas
• Cache Redis para performance

FASE 4 - MOBILE E ANALYTICS
• Aplicativo mobile React Native
• Dashboard de analytics
• Sistema de feedback dos usuários
• Integração com sistemas de pagamento

FASE 5 - INTELIGÊNCIA ARTIFICIAL
• Previsão de atrasos com ML
• Recomendações personalizadas
• Análise preditiva de demanda
• Chatbot para atendimento
```

### 🧪 **Slide - Melhorias Identificadas**
```
🧪 MELHORIAS PARA IMPLEMENTAR

TÉCNICAS:
• Testes automatizados (coverage > 90%)
• CI/CD com GitHub Actions
• Monitoramento com Sentry
• Documentação API com OpenAPI 3.0

FUNCIONAIS:
• Persistência de favoritos
• Modo offline para dados críticos
• Notificações em tempo real
• Integração com Google Maps

PERFORMANCE:
• Cache distribuído
• CDN para assets estáticos
• Otimização de queries
• Lazy loading de componentes
```

### 🎤 **Narração**
> "O projeto está bem estruturado para expansões futuras. Planejamos implementar funcionalidades avançadas como notificações push, aplicativo mobile e até mesmo inteligência artificial para previsão de atrasos. A arquitetura modular facilita a adição de novos recursos sem comprometer o código existente."

---

## ⏱️ 9:50 – 10:00 | 10. Encerramento

### 🎊 **Slide Final**
```
🎊 OBRIGADO!

PROJETO BUSFEED - PARTE 2
Sistema de Transporte Público do DF

RESULTADOS ALCANÇADOS:
✅ Sistema web completo e funcional
✅ Arquitetura escalável e manutenível
✅ Interface moderna e acessível
✅ Integração com dados geográficos
✅ APIs documentadas e testadas

TECNOLOGIAS DOMINADAS:
Django • React • PostgreSQL • PostGIS • Docker

Desenvolvido por: [Seu Nome]
GitHub: [seu-github]
LinkedIn: [seu-linkedin]
```

### 🎤 **Narração Final**
> "Concluímos com sucesso a Parte 2 do projeto BusFeed, entregando um sistema web completo e funcional. Implementamos uma arquitetura robusta, interfaces modernas e integrações com dados geográficos. O projeto demonstra domínio de tecnologias full stack e capacidade de resolver problemas reais do transporte público. Obrigado pela atenção! Lembrem-se de enviar o link deste vídeo através do AVA conforme orientações do professor."

---

## 📝 **Checklist de Gravação**

### ✅ **Antes de Gravar**
- [ ] Testar todos os serviços (frontend + backend)
- [ ] Verificar se o banco está populado com dados
- [ ] Preparar dados de teste para demonstração
- [ ] Configurar resolução de tela adequada
- [ ] Testar qualidade do áudio
- [ ] Preparar slides em ordem

### ✅ **Durante a Gravação**
- [ ] Falar de forma clara e pausada
- [ ] Seguir o tempo estipulado para cada seção
- [ ] Demonstrar funcionalidades sem pressa
- [ ] Destacar pontos técnicos importantes
- [ ] Manter energia e entusiasmo

### ✅ **Após a Gravação**
- [ ] Revisar o vídeo completo
- [ ] Verificar qualidade de áudio e vídeo
- [ ] Confirmar que todos os pontos foram cobertos
- [ ] Exportar em qualidade adequada
- [ ] Enviar pelo AVA dentro do prazo

---

## 🎯 **Dicas Importantes**

1. **Tempo**: Respeitar rigorosamente os 10 minutos
2. **Clareza**: Explicar conceitos técnicos de forma acessível
3. **Demonstração**: Mostrar o sistema funcionando, não apenas slides
4. **Profissionalismo**: Manter tom acadêmico e técnico
5. **Completude**: Cobrir todos os pontos do roteiro

---

*Roteiro completo para vídeo de 10 minutos - BusFeed Parte 2* 