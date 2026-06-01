# Usa exatamente a versão que seu ambiente atual está rodando para evitar quebras
FROM apache/airflow:3.1.0

# Altera para ROOT para instalar as dependências de sistema para o Chromium (.so)
USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgconf-2-4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libgdk-pixbuf2.0-0 \
    libgtk-3-0 \
    libgbm-dev \
    libnss3 \
    libxss1 \
    libasound2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Retorna para o usuário padrão seguro do Airflow
USER airflow

# Instala a biblioteca Python do Playwright
RUN pip install --no-cache-dir playwright

# Executa o download do binário do Chromium compatível
RUN playwright install chromium