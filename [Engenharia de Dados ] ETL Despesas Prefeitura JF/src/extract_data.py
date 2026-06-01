import os
from pathlib import Path
import logging
from datetime import datetime
from playwright.sync_api import sync_playwright

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("extract_data")

DIR_PROJECT = Path(__file__).resolve().parent.parent


def extract(data_execucao:str) -> Path:

    url_portal = "https://www.pjf.mg.gov.br/transparencia/dados_abertos/arquivos.php"
    
    ano_vigente = data_execucao[:4]
    mes_vigente = data_execucao[4:6]

    output_dir = DIR_PROJECT / "data" / "bronze" / f"ano={ano_vigente}" / f"mes={mes_vigente}"
    output_path = output_dir / f"despesas_{data_execucao}.csv"
    
    logger.info("Iniciando o processo de extração via automação de navegador.")
    logger.info(f"URL Alvo: {url_portal} | Ano Selecionado: {ano_vigente}")

    try:
        # Inicializa o contexto isolado do Playwright
        with sync_playwright() as p:
            logger.info("Lançando instância do Chromium em modo Headless...")
            browser = p.chromium.launch(headless=True, ignore_default_args=["--hide-scrollbars"])
            context = browser.new_context()
            page = context.new_page()
            
            # Navegação com tolerância a latências de rede
            logger.info("Acessando o portal de transparência...")
            page.goto(url_portal, timeout=60000, wait_until="networkidle")
            
            # Interação com os elementos do DOM
            logger.info(f"Definindo a opção do formulário para o ano: {ano_vigente}")
            page.select_option("select[name='ANO']", label=ano_vigente)
            
            logger.info("Disparando o clique de download e interceptando o evento de fluxo de rede...")
            with page.expect_download(timeout=45000) as download_info:
                # Utiliza o seletor baseado na função JavaScript avaliada para mitigar quebras de layout
                page.click("input[onclick*='despesas_csv']")
                
            download = download_info.value
            
            # Garante a existência do diretório destino (/data/bronze) antes da escrita
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Persiste o binário diretamente no volume mapeado
            logger.info(f"Download finalizado. Salvando dados na camada Bronze: {output_path}")
            download.save_as(str(output_path))
            
            # Fecha a instância para evitar vazamento de memória (Memory Leak) no container
            browser.close()
            
        logger.info(f"Extração e persistência concluídas com sucesso. Caminho do artefato: {output_path}")
        return output_path

    except Exception as e:
        logger.critical(f"Falha catastrófica durante a execução do Playwright: {str(e)}")
        raise