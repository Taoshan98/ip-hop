# Build stage for frontend
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/package*.json ./

# Install ALL dependencies (including devDependencies for build)
RUN npm ci

# Copy frontend source
COPY frontend/ ./

# Build frontend (needs TypeScript and other dev dependencies)
RUN npm run build

# Prune dev dependencies for production
RUN npm prune --omit=dev

# Build stage for backend
FROM python:3.12-alpine AS backend-builder

WORKDIR /app/backend

# Install build dependencies
RUN apk add --no-cache gcc musl-dev libffi-dev

# Copy requirements
COPY backend/requirements.txt ./

# Install Python dependencies in a virtual environment
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Final production stage
FROM python:3.12-alpine

LABEL maintainer="IP-HOP Team"
LABEL version="1.0.0"
LABEL description="IP-HOP DDNS Management Application"

# Install runtime dependencies only
RUN apk add --no-cache nodejs npm curl

# Create non-root user
RUN addgroup -g 1000 iphop && \
    adduser -D -u 1000 -G iphop iphop

WORKDIR /app

# Copy Python virtual environment from builder
COPY --from=backend-builder /opt/venv /opt/venv

# Copy backend application
COPY --chown=iphop:iphop backend/ /app/backend/

# Copy built frontend from builder
COPY --from=frontend-builder --chown=iphop:iphop /app/frontend/.next /app/frontend/.next
COPY --from=frontend-builder --chown=iphop:iphop /app/frontend/public /app/frontend/public
COPY --from=frontend-builder --chown=iphop:iphop /app/frontend/package*.json /app/frontend/
COPY --from=frontend-builder --chown=iphop:iphop /app/frontend/node_modules /app/frontend/node_modules

# Create database directory with proper permissions
RUN mkdir -p /app/backend/database && \
    chown -R iphop:iphop /app

# Switch to non-root user
USER iphop

# Set Python path
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH=/app

# Expose ports
EXPOSE 8001 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8001/api/v1/system/status || exit 1

# Copy startup script
COPY --chown=iphop:iphop docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

ENTRYPOINT ["/app/docker-entrypoint.sh"]
