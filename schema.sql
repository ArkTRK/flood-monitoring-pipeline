-- Criação da tabela de Cidades
CREATE TABLE cidades (
    id_cidade SERIAL PRIMARY KEY,
    nome_cidade VARCHAR(100) NOT NULL,
    uf CHAR(2) NOT NULL,
    latitude DECIMAL(9,6) NOT NULL,
    longitude DECIMAL(9,6) NOT NULL,
    altitude INT,
    timezone VARCHAR(50),
    risco_hidro_bas VARCHAR(20) -- Ex: Baixo, Moderado, Alto, Crítico
);

-- Criação da tabela de Histórico de Clima (Dados Brutos)
CREATE TABLE historico_clima (
    id_leitura SERIAL PRIMARY KEY,
    id_cidade INT REFERENCES cidades(id_cidade),
    data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    precipitacao DECIMAL(5,2),
    probabilidade_chuva DECIMAL(5,2),
    codigo_wmo INT
);

-- Criação da tabela de Insights (Dados processados pela IA)
CREATE TABLE insights_gemini (
    id_insight SERIAL PRIMARY KEY,
    id_cidade INT REFERENCES cidades(id_cidade),
    data_geracao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    nivel_risco VARCHAR(20),
    mensagem_alerta TEXT,
    recomendacao TEXT
);