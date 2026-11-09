FROM python:3.11-slim

RUN groupadd -r cvboost && useradd -r -g cvboost -d /app -s /sbin/nologin cvboost

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements-frontend.txt .
RUN pip install --no-cache-dir -r requirements-frontend.txt

COPY app.py .
COPY app/ app/

# Streamlit config
RUN mkdir -p /app/.streamlit
COPY streamlit_config.toml /app/.streamlit/config.toml

RUN chown -R cvboost:cvboost /app
USER cvboost

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s CMD curl -f http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "app/app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
