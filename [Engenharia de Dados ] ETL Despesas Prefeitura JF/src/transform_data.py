from pathlib import Path
import pandas as pd
import logging
import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("transform_data")

DIR_PROJECT = Path(__file__).resolve().parent.parent
OUTPUT_DIR_SILVER = DIR_PROJECT / "data" / "silver"

def transform(path_origem: Path) -> Path:
    logger.info(f"Iniciando a transformação dos dados. Origem: {path_origem}")

    if not path_origem.exists():
        logger.error(f"Arquivo bronze não encontrado para transformação: {path_origem}")
        raise FileNotFoundError(f"Origem ausente: {path_origem}")
    
    try:
        # Lemos a Bronze mantendo o padrão bruto
        df = pd.read_csv(path_origem, encoding="utf-8")
        logger.info(f"Dados carregados com sucesso. Total de linhas originais: [{len(df)}]")

        # =====================================================================
        # FLUXO DE TRANSFORMAÇÃO
        # =====================================================================
        df = padronizar_colunas(df)                    # 1º: Tudo vira snake_case imediatamente
        df = corrige_encoding(df)                      # 2º: Saneamento de caracteres
        df = drop_colunas_desnecessarias(df)           # 3º: Descarte de volumetria inútil
        df = transforma_colunas_para_numeric(df)       # 4º: Converte métricas financeiras
        df = transforma_para_data_correta(df)          # 5º: Converte e limpa campos temporais
        df = padronizacao_coluna_mes(df)               # 6º: Trata partições de mês
        df = remover_valores_nulos(df)                 # 7º: Elimina inconsistências críticas
        df = drop_duplicates(df)                       # 8º: Consolidação final de redundâncias

        # Garante a existência do diretório raiz da Silver
        OUTPUT_DIR_SILVER.mkdir(parents=True, exist_ok=True)
        logger.info(f"Salvando dados particionados na camada Silver: {OUTPUT_DIR_SILVER}")

        # Escrita performática usando o ecossistema PyArrow
        df.to_parquet(
            path=str(OUTPUT_DIR_SILVER),
            engine="pyarrow",
            compression='snappy',
            index=False,
            partition_cols=["ano", "mes"]
        )
        logger.info("Persistência na camada Silver concluída com sucesso.")

        return OUTPUT_DIR_SILVER

    except Exception as e:
        logger.critical(f"Falha catastrófica na transformação: {str(e)}")
        raise

# =====================================================================
# FUNÇÕES ESPECIALISTAS SUPORTE
# =====================================================================

def padronizar_colunas(df: pd.DataFrame) -> pd.DataFrame:
    df_copia = df.copy()
    # Remove espaços nas pontas, coloca em minúsculo e substitui espaços internos por sublinhado
    df_copia.columns = [col.strip().lower().replace(" ", "_") for col in df_copia.columns]
    logger.info("Nomes das colunas padronizados globalmente para snake_case.")
    return df_copia

def corrigir_double_encoding(texto: str) -> str:
    if not isinstance(texto, str) or not texto.strip():
        return texto
    try:
        return texto.encode('cp1252').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        try:
            return texto.encode('raw_unicode_escape').decode('utf-8')
        except Exception:
            return texto    

def corrige_encoding(df: pd.DataFrame) -> pd.DataFrame:
    coluna_problematica = "historico"
    if coluna_problematica in df.columns:
        logger.info(f"Saneando Double Encoding nativo da Bronze na coluna: {coluna_problematica}")
        df[coluna_problematica] = df[coluna_problematica].apply(corrigir_double_encoding)
        logger.info("Correção de caracteres finalizada.")
    return df

def drop_colunas_desnecessarias(df: pd.DataFrame) -> pd.DataFrame:
    # Mapeadas em snake_case para bater com a primeira transformação
    colunas_drop = [
        'ug', 'funcao', 'subfuncao', 'programa', 'programa_trabalho', 
        'categoria_economica', 'grupo_de_natureza_de_despesa', 
        'modalidade_de_aplicacao', 'elemento_de_despesa_orcamentaria',
        'natureza_de_despesa_com_subelemento', 'fonte'
    ]
    # Ignora colunas que porventura não existam para evitar quebras de KeyError
    existentes_drop = [col for col in colunas_drop if col in df.columns]
    return df.drop(columns=existentes_drop)

def transforma_colunas_para_numeric(df: pd.DataFrame) -> pd.DataFrame:
    numeric_cols = ['empenhado', 'liquidado', 'pago']
    actual_numeric_cols = [col for col in numeric_cols if col in df.columns]

    for col in actual_numeric_cols:
        # Correção do dtype: Verificamos se a coluna é do tipo textual (object ou string)
        if df[col].dtype == 'object' or isinstance(df[col].dtype, pd.StringDtype):
            df[col] = df[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
        
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
    return df

def transforma_para_data_correta(df: pd.DataFrame) -> pd.DataFrame:
    colunas_data = ['data_do_empenho', 'data_da_liquidacao']  # Ajustado para snake_case
    for col in colunas_data:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().replace(['-', '#N/A', 'nan', 'NAN'], np.nan)
            df[col] = pd.to_datetime(df[col], format='%m/%d/%y', errors='coerce')
    return df

def padronizacao_coluna_mes(df: pd.DataFrame) -> pd.DataFrame:
    if 'mes' in df.columns:
        df['mes'] = df['mes'].astype(str).str.strip().str.lower()
        mapeamento_meses = {
            "janeiro": "01", "fevereiro": "02", "março": "03", 
            "marã§o": "03", "mar%c3%a7o": "03", "abril": "04",
            "maio": "05", "junho": "06", "julho": "07", 
            "agosto": "08", "setembro": "09", "outubro": "10",
            "novembro": "11", "dezembro": "12"
        }
        df['mes'] = df['mes'].map(mapeamento_meses).fillna(df['mes'])
    return df

def remover_valores_nulos(df: pd.DataFrame) -> pd.DataFrame:
    linhas_drop = ['unidade_orcamentaria', 'nome_modalidade_de_aplicacao']
    existentes_subset = [col for col in linhas_drop if col in df.columns]
    return df.dropna(subset=existentes_subset)

def drop_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    linhas_antes = len(df)
    df_limpo = df.drop_duplicates()
    linhas_depois = len(df_limpo)

    logger.info(f"Remoção de duplicatas: {linhas_antes - linhas_depois} linhas duplicadas eliminadas.")
    return df_limpo