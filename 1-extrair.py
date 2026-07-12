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

print("Conexão com o banco de dados estabelecida com sucesso!")

# =====================================================================
# 2. DEFINIR AS CONFIGURAÇÕES DOS ARQUIVOS
# =====================================================================
caminho_arquivos = "banco_dados/" 

arquivos_tabelas = {
    "2025_Viagem.csv": "viagem",
    "2025_Passagem.csv": "passagem",
    "2025_Pagamento.csv": "pagamento",
    "2025_Trecho.csv": "trecho"
}

# =====================================================================
# 3. O TRADUTOR DE COLUNAS (DE: PARA)
# =====================================================================
tradutor_colunas = {
    # Comuns e Viagem
    'Identificador do processo de viagem': 'id_viagem',
    'Identificador do processo de viagem ': 'id_viagem', # Corrige o espaço invisível do Trecho!
    'Número da Proposta (PCDP)': 'num_proposta',
    'Situação': 'situacao',
    'Viagem Urgente': 'viagem_urgente',
    'Justificativa Urgência Viagem': 'justificativa_urgencia',
    'Código do órgão superior': 'cod_orgao_superior',
    'Nome do órgão superior': 'nome_orgao_superior',
    'CPF viajante': 'cpf_viajante',
    'Nome': 'nome_viajante',
    'Cargo': 'cargo',
    'Função': 'funcao',
    'Descrição Função': 'descricao_funcao',
    'Período - Data de início': 'data_inicio',
    'Período - Data de fim': 'data_fim',
    'Destinos': 'destinos',
    'Motivo': 'motivo',
    'Valor diárias': 'valor_diarias',
    'Valor passagens': 'valor_passagens',
    'Valor devolução': 'valor_devolucao',
    'Valor outros gastos': 'valor_outros_gastos',
    
    # Passagem
    'Meio de transporte': 'meio_transporte',
    'País - Origem ida': 'pais_origem_ida',
    'UF - Origem ida': 'uf_origem_ida',
    'Cidade - Origem ida': 'cidade_origem_ida',
    'País - Destino ida': 'pais_destino_ida',
    'UF - Destino ida': 'uf_destino_ida',
    'Cidade - Destino ida': 'cidade_destino_ida',
    'País - Origem volta': 'pais_origem_volta',
    'UF - Origem volta': 'uf_origem_volta',
    'Cidade - Origem volta': 'cidade_origem_volta',
    'Pais - Destino volta': 'pais_destino_volta',
    'UF - Destino volta': 'uf_destino_volta',
    'Cidade - Destino volta': 'cidade_destino_volta',
    'Valor da passagem': 'valor_passagem',
    'Taxa de serviço': 'taxa_servico',
    'Data da emissão/compra': 'data_emissao',
    'Hora da emissão/compra': 'hora_emissao',
    
    # Pagamento
    'Codigo do órgão pagador': 'cod_orgao_pagador',
    'Nome do órgao pagador': 'nome_orgao_pagador',
    'Código da unidade gestora pagadora': 'cod_ug_pagadora',
    'Nome da unidade gestora pagadora': 'nome_ug_pagadora',
    'Tipo de pagamento': 'tipo_pagamento',
    'Valor': 'valor',
    
    # Trecho
    'Sequência Trecho': 'sequencia_trecho',
    'Origem - Data': 'origem_data',
    'Origem - País': 'origem_pais',
    'Origem - UF': 'origem_uf',
    'Origem - Cidade': 'origem_cidade',
    'Destino - Data': 'destino_data',
    'Destino - País': 'destino_pais',
    'Destino - UF': 'destino_uf',
    'Destino - Cidade': 'destino_cidade',
    'Número Diárias': 'numero_diarias',
    'Missao?': 'missao'
}

# =====================================================================
# 4. FUNÇÃO DE EXTRAÇÃO E CARGA (ETL - CAMADA RAW)
# =====================================================================
def carregar_dados_raw():
    for arquivo, tabela in arquivos_tabelas.items():
        caminho_completo = os.path.join(caminho_arquivos, arquivo)
        
        print(f"\nIniciando o processamento do arquivo: {arquivo}")
        
        try:
            with engine.connect() as conn:
                conn.execute(text(f"TRUNCATE TABLE raw.{tabela} CASCADE;"))
                conn.commit() 
                print(f"Tabela raw.{tabela} limpa (TRUNCATE executado).")
            
            chunks = pd.read_csv(
                caminho_completo, 
                sep=';', 
                encoding='latin-1', 
                dtype=str, 
                chunksize=10000 
            )
            
            linhas_inseridas = 0
            
            for chunk in chunks:
                # 1. Renomeia as colunas usando o nosso tradutor
                chunk = chunk.rename(columns=tradutor_colunas)
                
                # 2. Remove as colunas surpresas que o governo enviou e que não estão no SQL
                colunas_extras = ['Código órgão solicitante', 'Nome órgão solicitante']
                chunk = chunk.drop(columns=colunas_extras, errors='ignore')

                # 3. Envia os dados limpos e traduzidos para o banco
                chunk.to_sql(
                    name=tabela, 
                    con=engine, 
                    schema='raw', 
                    if_exists='append', 
                    index=False
                )
                linhas_inseridas += len(chunk)
                print(f"  -> {linhas_inseridas} linhas inseridas em raw.{tabela}...")
                
            print(f"SUCESSO: Arquivo {arquivo} carregado totalmente em raw.{tabela}!")
            
        except FileNotFoundError:
            print(f"ERRO: O arquivo {arquivo} não foi encontrado na pasta {caminho_arquivos}.")
        except Exception as e:
            print(f"ERRO inesperado ao processar {arquivo}: {e}")

if __name__ == "__main__":
    carregar_dados_raw()
    print("\nProcesso de Extração da Fase 1 finalizado!")