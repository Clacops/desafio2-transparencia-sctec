import pandas as pd
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

# =====================================================================
# 1. CARREGAR CREDENCIAIS E CONECTAR AO BANCO
# =====================================================================
load_dotenv() 

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Cria o "motor" de conexão com o PostgreSQL
string_conexao = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(string_conexao)

# =====================================================================
# 2. FUNÇÕES DE LIMPEZA GERAL
# =====================================================================
def limpar_moeda(valor):
    """Remove vírgulas e pontos do texto e converte para número decimal"""
    if pd.isna(valor) or str(valor).strip() == '':
        return 0.0
    
    texto = str(valor).replace('.', '').replace(',', '.')
    
    try:
        numero = float(texto)
        return numero if numero >= 0 else 0.0 
    except ValueError:
        return 0.0

def limpar_data(serie_data):
    """Converte o texto DD/MM/AAAA para o formato oficial de Data do Banco"""
    return pd.to_datetime(serie_data, format='%d/%m/%Y', errors='coerce')

# =====================================================================
# 3. EXTRAIR DA RAW, TRANSFORMAR E CARREGAR NA SILVER
# =====================================================================
def transformar_dados():
    print("\nIniciando o processo de Transformação (Fase 2)...")
    
    # ---------------------------------------------------------
    # Preparação da Infraestrutura
    # ---------------------------------------------------------
    # 1. Garante que a pasta (schema) silver existe
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS silver;"))
        conn.commit()

    # 2. Tenta limpar os dados antigos. Se a tabela não existir, engole o erro e segue em frente.
    try:
        with engine.connect() as conn:
            conn.execute(text("TRUNCATE TABLE silver.viagem CASCADE;"))
            conn.commit()
            print("Tabelas antigas da camada Silver limpas com sucesso.")
    except Exception:
        print("Primeira execução detectada: As tabelas Silver serão criadas agora.")

    # =========================================================
    # TABELA 1: VIAGEM 
    # =========================================================
    print("\n[1/4] Processando e limpando dados de VIAGEM...")
    df_silver_viagem = pd.read_sql("SELECT * FROM raw.viagem", con=engine)
    
    df_silver_viagem = df_silver_viagem.dropna(subset=['id_viagem'])
    df_silver_viagem = df_silver_viagem.drop_duplicates(subset=['id_viagem']) 
    df_silver_viagem['nome_orgao_superior'] = df_silver_viagem['nome_orgao_superior'].fillna('NÃO INFORMADO')
    df_silver_viagem['data_inicio'] = limpar_data(df_silver_viagem['data_inicio'])
    df_silver_viagem['data_fim'] = limpar_data(df_silver_viagem['data_fim'])

    colunas_moeda = ['valor_diarias', 'valor_passagens', 'valor_devolucao', 'valor_outros_gastos']
    for col in colunas_moeda:
        df_silver_viagem[col] = df_silver_viagem[col].apply(limpar_moeda)

    df_silver_viagem['valor_total'] = df_silver_viagem['valor_diarias'] + df_silver_viagem['valor_passagens'] + df_silver_viagem['valor_devolucao'] + df_silver_viagem['valor_outros_gastos']
    df_silver_viagem['duracao_dias'] = (df_silver_viagem['data_fim'] - df_silver_viagem['data_inicio']).dt.days
    df_silver_viagem['duracao_dias'] = df_silver_viagem['duracao_dias'].fillna(0).astype(int)

    colunas_silver_viagem = ['id_viagem', 'num_proposta', 'situacao', 'viagem_urgente', 'cod_orgao_superior', 'nome_orgao_superior', 'nome_viajante', 'cargo', 'data_inicio', 'data_fim', 'destinos', 'motivo', 'valor_diarias', 'valor_passagens', 'valor_devolucao', 'valor_outros_gastos', 'valor_total', 'duracao_dias']
    df_silver_viagem = df_silver_viagem[colunas_silver_viagem]

    df_silver_viagem.to_sql('viagem', con=engine, schema='silver', if_exists='append', index=False)
    print(f"  -> {len(df_silver_viagem)} viagens perfeitas inseridas em silver.viagem.")

    ids_validos = df_silver_viagem['id_viagem'].tolist()

    # =========================================================
    # TABELA 2: PASSAGEM 
    # =========================================================
    print("[2/4] Processando e limpando dados de PASSAGEM...")
    df_silver_passagem = pd.read_sql("SELECT * FROM raw.passagem", con=engine)
    df_silver_passagem = df_silver_passagem[df_silver_passagem['id_viagem'].isin(ids_validos)]

    df_silver_passagem['data_emissao'] = limpar_data(df_silver_passagem['data_emissao'])
    df_silver_passagem['valor_passagem'] = df_silver_passagem['valor_passagem'].apply(limpar_moeda)
    df_silver_passagem['taxa_servico'] = df_silver_passagem['taxa_servico'].apply(limpar_moeda)

    colunas_silver_passagem = ['id_viagem', 'meio_transporte', 'pais_origem_ida', 'uf_origem_ida', 'cidade_origem_ida', 'pais_destino_ida', 'uf_destino_ida', 'cidade_destino_ida', 'valor_passagem', 'taxa_servico', 'data_emissao']
    df_silver_passagem = df_silver_passagem[colunas_silver_passagem]

    df_silver_passagem.to_sql('passagem', con=engine, schema='silver', if_exists='append', index=False)
    print(f"  -> {len(df_silver_passagem)} passagens perfeitas inseridas em silver.passagem.")

    # =========================================================
    # TABELA 3: PAGAMENTO 
    # =========================================================
    print("[3/4] Processando e limpando dados de PAGAMENTO...")
    df_silver_pagamento = pd.read_sql("SELECT * FROM raw.pagamento", con=engine)
    df_silver_pagamento = df_silver_pagamento[df_silver_pagamento['id_viagem'].isin(ids_validos)]

    df_silver_pagamento['tipo_pagamento'] = df_silver_pagamento['tipo_pagamento'].fillna('NÃO INFORMADO')
    df_silver_pagamento['valor'] = df_silver_pagamento['valor'].apply(limpar_moeda)

    colunas_silver_pagamento = ['id_viagem', 'num_proposta', 'nome_orgao_pagador', 'nome_ug_pagadora', 'tipo_pagamento', 'valor']
    df_silver_pagamento = df_silver_pagamento[colunas_silver_pagamento]

    df_silver_pagamento.to_sql('pagamento', con=engine, schema='silver', if_exists='append', index=False)
    print(f"  -> {len(df_silver_pagamento)} pagamentos perfeitos inseridos em silver.pagamento.")

    # =========================================================
    # TABELA 4: TRECHO 
    # =========================================================
    print("[4/4] Processando e limpando dados de TRECHO...")
    df_silver_trecho = pd.read_sql("SELECT * FROM raw.trecho", con=engine)
    df_silver_trecho = df_silver_trecho[df_silver_trecho['id_viagem'].isin(ids_validos)]

    df_silver_trecho = df_silver_trecho.dropna(subset=['sequencia_trecho'])
    df_silver_trecho['sequencia_trecho'] = pd.to_numeric(df_silver_trecho['sequencia_trecho'], errors='coerce').fillna(0).astype(int)
    df_silver_trecho = df_silver_trecho.drop_duplicates(subset=['id_viagem', 'sequencia_trecho']) 

    df_silver_trecho['origem_data'] = limpar_data(df_silver_trecho['origem_data'])
    df_silver_trecho['destino_data'] = limpar_data(df_silver_trecho['destino_data'])
    df_silver_trecho['numero_diarias'] = df_silver_trecho['numero_diarias'].apply(limpar_moeda)

    colunas_silver_trecho = ['id_viagem', 'sequencia_trecho', 'origem_data', 'origem_uf', 'origem_cidade', 'destino_data', 'destino_uf', 'destino_cidade', 'meio_transporte', 'numero_diarias']
    df_silver_trecho = df_silver_trecho[colunas_silver_trecho]

    df_silver_trecho.to_sql('trecho', con=engine, schema='silver', if_exists='append', index=False)
    print(f"  -> {len(df_silver_trecho)} trechos perfeitos inseridos em silver.trecho.")

if __name__ == "__main__":
    transformar_dados()
    print("\nSUCESSO: Pipeline da Fase 2 (Camada Silver) finalizado!")