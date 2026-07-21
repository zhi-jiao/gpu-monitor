# Stage 1: build the React frontend
FROM node:24-slim AS frontend-builder

WORKDIR /app/web
COPY web/package.json web/package-lock.json ./
RUN npm ci

COPY web/ ./
RUN npm run build

# Stage 2: Python runtime with the built frontend
FROM python:3.10-slim AS runtime

WORKDIR /app

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY agent ./agent
COPY app ./app
COPY servers.json ./
COPY tests ./tests
COPY pyproject.toml ./

# Copy the built frontend from the Node stage
COPY --from=frontend-builder /app/web/dist ./web/dist

# Dashboard port
EXPOSE 8888

CMD ["python", "app/main.py"]
