FROM python:3.11-slim
WORKDIR /app
COPY webapp/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY phyto_discover_core/ ./phyto_discover_core/
COPY webapp/backend/ ./webapp/backend/
COPY cli/ ./cli/
COPY data/ ./data/
ENV PYTHONPATH=/app
EXPOSE 8001
CMD ["python", "-m", "uvicorn", "webapp.backend.main:app", "--host", "0.0.0.0", "--port", "8001"]
