import logging
import pendulum
import pandas as pd
from pathlib import Path
from airflow.decorators import dag, task
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.utils.trigger_rule import TriggerRule


from src.extract_data import extract as run_extract
from src.transform_data import transform as run_transform
from src.load_data import load as run_load

logger = logging.getLogger("airflow.task")

@dag(
    schedule=None,
    start_date=pendulum.datetime(2026, 5, 26, tz="America/Sao_Paulo"),
    catchup=False,
    tags=["despesas"]
)
def PipelineDespesas():

    @task(task_id="enviar_email_falha", trigger_rule=TriggerRule.ONE_FAILED)
    def enviar_email():
    # Aqui entra o seu código de envio de e-mail (ex: EmailOperator ou SMTP)
        logger.info("Enviando e-mail de alerta...")

    @task(task_id="extracao_dados")
    def extract_task(ds_nodash=None):
        logger.info("Executando módulo de extração bruto...")
        caminho_bronze = run_extract(data_execucao= ds_nodash)
        return str(caminho_bronze)
        
    @task(task_id="transforma_dados")
    def transform_task(caminho_bronze_recebido:str):
        logger.info("Executando módulo de transformação e limpeza...")
        caminho_silver = run_transform(path_origem=Path(caminho_bronze_recebido))
        return str(caminho_silver)
    
    @task
    def validate_data(path_silver: str) -> str:
        """
        Task de Data Quality Gate. Avalia a integridade do arquivo
        antes de permitir a progressão para a camada Gold.
        """
        logger.info(f"Iniciando checagem de qualidade no caminho: {path_silver}")
        
        try:
            df = pd.read_parquet(path_silver)
            
            # Teste de Volumetria Crítica
            if len(df) == 0:
                raise ValueError("O DataFrame gerado na camada Silver está completamente vazio.")
                
            # Teste de Inconsistência de Colunas
            colunas_obrigatorias = ['historico', 'empenhado', 'ano', 'mes']
            for col in colunas_obrigatorias:
                if col not in df.columns:
                    raise KeyError(f"Coluna mandatória ausente no arquivo transformado: {col}")
                    
            # Teste de Sanidade Financeira (Evita estouro de valores zerados por falha de replace)
            if df['empenhado'].sum() == 0 and df['liquidado'].sum() == 0:
                logger.warning("Alerta: O somatório das colunas financeiras resultou em zero. Validar a fonte.")
                
            logger.info(f"Data Quality Gate aprovado com sucesso para {len(df)} linhas.")
            return path_silver

        except Exception as e:
            logger.error(f"Qualidade dos dados rejeitada: {str(e)}")
            raise AirflowFailException(f"Pipeline interceptado pelo Quality Gate: {str(e)}")

    @task(task_id="carrega_dados")
    def load_task(caminho_silver_recebido:str) -> None:
        logger.info("Executando módulo de carga analítica...")
        run_load(path_origem_silver=Path(caminho_silver_recebido))

    
    start = EmptyOperator(task_id="start")
    end = EmptyOperator(task_id="end", trigger_rule=TriggerRule.ALL_DONE)
    
    enviar_email_falha = enviar_email()

    
    extracao = extract_task()
    transformacao = transform_task(extracao)
    valida = validate_data(transformacao)
    carrega = load_task(valida)

    # Definindo a ordem de execução sequencial pura (Sem passagem de XCom)
    start >> extracao >> transformacao >> valida >> carrega >> end

    extracao >> enviar_email_falha 
    transformacao >> enviar_email_falha 
    carrega >> enviar_email_falha

    enviar_email_falha >> end
    

PipelineDespesas()