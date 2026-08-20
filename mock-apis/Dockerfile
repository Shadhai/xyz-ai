# infrastructure/docker/docker-compose.yml
version: '3.8'

services:
  # AI Engine
  ai-engine:
    build:
      context: ../../ai-engine
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379
      - MONGODB_URI=mongodb://mongodb:27017/xyz-ai
    depends_on:
      - redis
      - mongodb
    volumes:
      - ../../ai-engine/models:/app/models
    networks:
      - xyz-ai-network

  # Backend API
  backend:
    build:
      context: ../../backend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - AI_ENGINE_URL=http://ai-engine:8000
      - REDIS_URL=redis://redis:6379
      - MONGODB_URI=mongodb://mongodb:27017/xyz-ai
    depends_on:
      - ai-engine
      - redis
      - mongodb
    networks:
      - xyz-ai-network

  # Frontend
  frontend:
    build:
      context: ../../frontend
      dockerfile: Dockerfile
    ports:
      - "8080:80"
    depends_on:
      - backend
    networks:
      - xyz-ai-network

  # Redis Cache
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    networks:
      - xyz-ai-network

  # MongoDB
  mongodb:
    image: mongo:7
    ports:
      - "27017:27017"
    volumes:
      - mongodb-data:/data/db
    networks:
      - xyz-ai-network

  # Monitoring
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    volumes:
      - grafana-data:/var/lib/grafana
    networks:
      - xyz-ai-network

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ../../monitoring/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
    networks:
      - xyz-ai-network

volumes:
  redis-data:
  mongodb-data:
  grafana-data:

networks:
  xyz-ai-network:
    driver: bridge