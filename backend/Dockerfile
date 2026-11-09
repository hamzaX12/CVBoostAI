FROM python:3.11-slim

# Security: non-root user
RUN groupadd -r cvboost && useradd -r -g cvboost -d /app -s /sbin/nologin cvboost

# System deps (WeasyPrint, pdfplumber, pytesseract)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-fra \
    tesseract-ocr-ara \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -e ".[dev]" \
    && pip install --no-cache-dir html2text

# Copy app
COPY app/ app/
COPY migrations/ migrations/

# Create upload directory
RUN mkdir -p /app/uploads && chown cvboost:cvboost /app/uploads

# Switch to non-root user
USER cvboost

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
  CMD curl -f http://localhost:8000/api/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--loop", "asyncio"]
