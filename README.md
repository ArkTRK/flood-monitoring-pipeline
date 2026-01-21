# 🌊 Smart Flood Monitoring Pipeline (ETL + AI)

Este projeto é um pipeline de dados **ETL (Extract, Transform, Load)** desenvolvido para monitorar riscos de enchentes em tempo real. O sistema extrai dados meteorológicos de alta precisão, utiliza Inteligência Artificial para analisar o contexto geográfico e armazena insights estruturados em um banco de dados PostgreSQL.

## 🚀 Funcionalidades

- **Extração Dinâmica:** Consome dados da API Open-Meteo para cidades cadastradas em um banco de dados relacional.
- **Análise Histórica e Preditiva:** Calcula o acumulado de chuva das últimas 24h (saturação do solo) e a previsão para as próximas 3h.
- **Inteligência Artificial:** Integração com **Google Gemini AI** para gerar alertas humanizados e níveis de risco (Baixo, Moderado, Alto, Crítico).
- **Persistência de Dados:** Armazena o histórico técnico e os insights da IA para futuras análises de dados.

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python 3.11+
- **Banco de Dados:** PostgreSQL
- **IA:** Google Gemini API (`gemini-2.5-flash-lite`)
- **APIs de Clima:** Open-Meteo
- **Bibliotecas Principais:** `psycopg2`, `pandas`, `google-generativeai`, `requests-cache`

## 📋 Pré-requisitos

Antes de iniciar, você precisará ter:
- Um servidor PostgreSQL ativo.
- Uma chave de API do Google Gemini.
- Python instalado no seu ambiente (Ubuntu/Windows).

## 🔧 Configuração

1. **Clone o repositório:**
   
   git clone [https://github.com/seu-usuario/seu-repositorio.git](https://github.com/seu-usuario/seu-repositorio.git)
   cd seu-repositorio

2. **Instale as dependências**
   
   pip install -r requirements.txt
  
3. **Configure as Variáveis de Ambiente**
Crie um arquivo .env baseado no exemplo abaixo:

DB_HOST=seu_ip
DB_NAME=weather_db
DB_USER=seu_usuario
DB_PASS=sua_senha
DB_PORT=5432
GEMINI_API_KEY=sua_chave_aqui

4. **Prepare o Banco de Dados**
Execute os scripts SQL disponíveis em schema.sql para criar as tabelas cidades, historico_clima e insights_gemini.

**Exemplo de Saída**
📍 Processando: RIO DE JANEIRO
   📊 Dados Brutos: Acumulado 24h: 45.20mm | Previsão 3h: 12.50mm

   🤖 ANÁLISE DO GEMINI:
      ● Risco: Alto
      ● Alerta: Risco iminente de alagamentos em áreas de encosta e regiões baixas.
      ● Ação: Evite áreas com histórico de inundação e atente para os sinais de alerta da Defesa Civil.

   💾 Dados persistidos no PostgreSQL.

## 🏗️ Infraestrutura e Execução

O projeto foi desenvolvido e testado utilizando a seguinte infraestrutura:

### Minha Stack Atual
* **Servidor:** Ubuntu Server (Execução do script Python e hospedagem do banco).
* **Banco de Dados:** PostgreSQL (Instância local no servidor).

### Sugestões de Evolução (Cloud)
Para cenários de alta disponibilidade e escala, o projeto pode ser migrado para:
* **AWS:** AWS Lambda para execução do script (Serverless) + Amazon RDS para o PostgreSQL.
* **Google Cloud:** Cloud Functions + Cloud SQL.
* **Docker:** Containerização da aplicação para facilitar o deploy em qualquer ambiente (incluído `Dockerfile` como melhoria futura).

## 🛠️ Execução no Ambiente de Desenvolvimento

Para validar o pipeline e visualizar os alertas em tempo real:
1. Abra o projeto no **VS Code**.
2. Certifique-se de que o banco PostgreSQL está rodando no seu servidor ou localhost.
3. Execute o script principal:
   ```bash
   python main.py
