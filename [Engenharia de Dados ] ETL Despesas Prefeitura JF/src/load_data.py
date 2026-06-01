from pathlib import Path
import pandas as pd
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("load_data")

DIR_PROJECT = Path(__file__).resolve().parent.parent
GOLD_DIR = DIR_PROJECT / "data" / "gold"

def load(path_origem_silver: Path) -> None:
    logger.info(f"Iniciando a carga dimensional completa na Gold. Origem: {path_origem_silver}")
    
    if not path_origem_silver.exists():
        logger.error(f"Arquivo Silver não encontrado para carga: {path_origem_silver}")
        raise FileNotFoundError(f"Origem ausente: {path_origem_silver}")
    
    try:
        # 1. Lê os dados unificados da Silver (ou do estágio atual)
        df_silver = pd.read_parquet(path_origem_silver, engine="pyarrow")
        logger.info(f"Dados carregados. Total de linhas para processamento: [{len(df_silver)}]")
        
        GOLD_DIR.mkdir(parents=True, exist_ok=True)

        # Trata possíveis nulos em colunas textuais de dimensões para não quebrar chaves
        colunas_texto_dim = ['unidade_orcamentaria', 'categoria', 'nome_ug', 'nome_da_funcao', 'nome_modalidade_de_aplicacao']
        for col in colunas_texto_dim:
            if col in df_silver.columns:
                df_silver[col] = df_silver[col].fillna("NÃO INFORMADO")

        # =====================================================================
        # 2. CRIAÇÃO DA DIMENSÃO: UNIDADES
        # =====================================================================
        cols_unidades = ['unidade_orcamentaria', 'categoria', 'nome_ug']
        dim_unidades = df_silver[cols_unidades].drop_duplicates().reset_index(drop=True)
        dim_unidades['sk_unidade'] = dim_unidades.index + 1
        
        path_dim_unidades = GOLD_DIR / "dim_unidades.parquet"
        dim_unidades.to_parquet(path_dim_unidades, engine="pyarrow", index=False)
        logger.info(f"Dimensão 'dim_unidades' persistida: {path_dim_unidades}")

        # =====================================================================
        # 3. CRIAÇÃO DA DIMENSÃO: FUNÇÕES
        # =====================================================================
        cols_funcoes = ['nome_da_funcao', 'nome_modalidade_de_aplicacao']
        dim_funcoes = df_silver[cols_funcoes].drop_duplicates().reset_index(drop=True)
        dim_funcoes['sk_funcao'] = dim_funcoes.index + 1
        
        path_dim_funcoes = GOLD_DIR / "dim_funcoes.parquet"
        dim_funcoes.to_parquet(path_dim_funcoes, engine="pyarrow", index=False)
        logger.info(f"Dimensão 'dim_funcoes' persistida: {path_dim_funcoes}")

        # =====================================================================
        # 4. CRIAÇÃO DA TABELA FATO: DESPESAS
        # =====================================================================
        # Mapeia a SK de Unidades
        df_fato = df_silver.merge(dim_unidades, on=cols_unidades, how='left')
        
        # Mapeia a SK de Funções
        df_fato = df_fato.merge(dim_funcoes, on=cols_funcoes, how='left')
        
        # Isolamos apenas as chaves, campos de data/tempo e as métricas financeiras
        colunas_finais_fato = [
            'sk_unidade', 
            'sk_funcao', 
            'data_do_empenho', 
            'data_da_liquidacao', 
            'ano', 
            'mes', 
            'empenhado', 
            'liquidado', 
            'pago', 
            'historico'
        ]
        
        # Garante que só vamos selecionar colunas que realmente existem no DataFrame
        fato_despesas = df_fato[[col for col in colunas_finais_fato if col in df_fato.columns]]
        
        path_fato = GOLD_DIR / "gold_despesas.parquet"
        fato_despesas.to_parquet(path_fato, engine="pyarrow", index=False)
        logger.info(f"Tabela Fato 'fato_despesas' consolidada com sucesso: {path_fato}")

    except Exception as e:
        logger.critical(f"Falha catastrófica na modelagem da camada Gold: {str(e)}")
        raise