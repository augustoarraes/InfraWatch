# Imagem leve baseada no Alpine
FROM python:3.10-alpine

# Variáveis de ambiente para o Streamlit
ENV PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ENABLECORS=false

# Definir diretório de trabalho
WORKDIR /app

RUN apk update && \
    apk add --no-cache \
      build-base \
      bash \
      traceroute \
      tcptraceroute \
      mtr \
      iproute2 \
      bash \
      curl \
      gcc \
      g++ \
      musl-dev \
      linux-headers \
      python3-dev

# Copiar e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o app
COPY . .

# Expor porta do Streamlit
EXPOSE 8501

# Comando padrão para iniciar o Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
