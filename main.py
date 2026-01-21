import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry
import os
import psycopg2
import json
from dotenv import load_dotenv
import google.generativeai as genai

# CONFIGURAÇÕES INICIAIS
load_dotenv()

# Configura o Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash-lite')

# Configura Open-Meteo (Cache e Retry)
cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# Conexão com o BD
def obter_conexao():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        port=os.getenv("DB_PORT")
    )

def obter_cidades_para_monitoramento():
    try:
        conn = obter_conexao()
        cursor = conn.cursor()
        query = "SELECT id_cidade, nome_cidade, uf, latitude, longitude, altitude, timezone, risco_hidro_base FROM cidades;"
        cursor.execute(query)
        colunas = [desc[0] for desc in cursor.description]
        cidades = [dict(zip(colunas, row)) for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return cidades
    except Exception as e:
        print(f"❌ Erro ao ler cidades no banco: {e}")
        return []

def salvar_historico_clima(id_cidade, precipitacao, probabilidade, codigo_wmo):
    try:
        conn = obter_conexao()
        cursor = conn.cursor()
        query = """
            INSERT INTO historico_clima (id_cidade, data_hora, precipitacao, probabilidade_chuva, codigo_wmo)
            VALUES (%s, CURRENT_TIMESTAMP, %s, %s, %s);
        """
        cursor.execute(query, (id_cidade, precipitacao, probabilidade, codigo_wmo))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ Erro ao salvar histórico: {e}")

def salvar_e_exibir_insight(id_cidade, insight_json):
    """Processa o JSON da IA, exibe na tela e salva no banco."""
    try:
        # Limpeza para garantir JSON puro
        limpo = insight_json.replace("```json", "").replace("```", "").strip()
        dados = json.loads(limpo)
        
        # Exibição detalhada no console
        print(f"\n   🤖 ANÁLISE DO GEMINI:")
        print(f"      ● Risco: {dados.get('nivel_risco')}")
        print(f"      ● Alerta: {dados.get('mensagem_alerta')}")
        print(f"      ● Ação: {dados.get('recomendacao')}")

        # Salva no Banco
        conn = obter_conexao()
        cursor = conn.cursor()
        query = """
            INSERT INTO insights_gemini (id_cidade, data_geracao, nivel_risco, mensagem_alerta, recomendacao)
            VALUES (%s, CURRENT_TIMESTAMP, %s, %s, %s);
        """
        cursor.execute(query, (
            id_cidade, 
            dados.get('nivel_risco'), 
            dados.get('mensagem_alerta'), 
            dados.get('recomendacao')
        ))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"   💾 Dados persistidos no PostgreSQL.")

    except Exception as e:
        print(f"❌ Erro no processamento do Insight: {e}")
        print(f"Conteúdo bruto recebido: {insight_json}")

# Inteligência e revisão (lógica)
def gerar_insight_gemini(dados_cidade, acumulado, previsao):
    prompt = f"""
    Atue como um Engenheiro de Defesa Civil. 
    Analise o risco de enchente para {dados_cidade['nome_cidade']}-{dados_cidade['uf']}.
    Contexto: Altitude {dados_cidade['altitude']}m, Risco Base {dados_cidade['risco_hidro_base']}.
    Dados: Acumulado 24h: {acumulado:.2f}mm, Previsão próximas 3h: {previsao:.2f}mm.
    
    Retorne APENAS um JSON:
    {{
        "nivel_risco": "Baixo/Moderado/Alto/Crítico",
        "mensagem_alerta": "frase curta e impactante",
        "recomendacao": "orientação direta"
    }}
    """
    response = model.generate_content(prompt)
    return response.text

# Oquestração do pipeline
def executar_pipeline(cidades):
    url = "https://api.open-meteo.com/v1/forecast"
    for cidade in cidades:
        try:
            print(f"\n--- MONITORANDO: {cidade['nome_cidade'].upper()} ---")
            
            params = {
                "latitude": cidade['latitude'], "longitude": cidade['longitude'],
                "hourly": ["precipitation", "precipitation_probability", "weather_code"],
                "timezone": cidade['timezone'], "past_days": 1, "forecast_days": 1
            }
            
            responses = openmeteo.weather_api(url, params=params)
            res = responses[0]
            hourly = res.Hourly()
            
            # Dados da API
            precipitacao = hourly.Variables(0).ValuesAsNumpy()
            probabilidade = hourly.Variables(1).ValuesAsNumpy()
            wmo = hourly.Variables(2).ValuesAsNumpy()
            
            # Cálculos de Janela
            acum_24h = sum(precipitacao[:24])
            prev_3h = sum(precipitacao[24:27])
            
            print(f"   📊 Dados Brutos: Acumulado 24h: {acum_24h:.2f}mm | Previsão 3h: {prev_3h:.2f}mm")
            
            # IA e Persistência
            insight = gerar_insight_gemini(cidade, acum_24h, prev_3h)
            salvar_historico_clima(cidade['id_cidade'], float(precipitacao[24]), float(probabilidade[24]), int(wmo[24]))
            salvar_e_exibir_insight(cidade['id_cidade'], insight)
            
        except Exception as e:
            print(f"❌ Falha no processamento de {cidade['nome_cidade']}: {e}")

if __name__ == "__main__":
    print("🚀 SISTEMA DE MONITORAMENTO DE ENCHENTES INICIADO")
    cidades = obter_cidades_para_monitoramento()
    
    if cidades:
        executar_pipeline(cidades)
    
    print("\n🏁 Processamento concluído.")