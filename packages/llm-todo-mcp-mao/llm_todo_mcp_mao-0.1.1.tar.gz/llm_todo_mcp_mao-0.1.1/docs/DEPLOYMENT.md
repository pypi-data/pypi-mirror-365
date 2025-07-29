# Deployment Guide

This guide covers various deployment scenarios for the Todo MCP Server, from development to production environments.

## Table of Contents

- [Development Deployment](#development-deployment)
- [Production Deployment](#production-deployment)
- [Docker Deployment](#docker-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Monitoring & Maintenance](#monitoring--maintenance)
- [Security Considerations](#security-considerations)

## Development Deployment

### Local Development Setup

1. **Clone and Setup**
```bash
git clone <repository-url>
cd todo-mcp
uv sync --dev
```

2. **Configuration**
```bash
# Create development configuration
cat > .env << EOF
TODO_MCP_ENVIRONMENT=development
TODO_MCP_DATA_DIRECTORY=./dev-data
TODO_MCP_LOG_LEVEL=DEBUG
TODO_MCP_BACKUP_ENABLED=true
TODO_MCP_PERFORMANCE_MONITORING=true
EOF
```

3. **Start Development Server**
```bash
uv run todo-mcp-server --log-level DEBUG
```

### Development with Hot Reload

For development with automatic reloading:

```bash
# Install watchdog for file monitoring
uv add --dev watchdog

# Start with file watching
uv run todo-mcp-server --file-watch
```

## Production Deployment

### System Requirements

**Minimum Requirements:**
- CPU: 1 core, 2.0 GHz
- RAM: 512 MB
- Storage: 1 GB available space
- OS: Linux (Ubuntu 20.04+), macOS, Windows Server

**Recommended for Production:**
- CPU: 2+ cores, 2.4 GHz
- RAM: 2 GB
- Storage: 10 GB SSD
- OS: Linux (Ubuntu 22.04 LTS)

### Production Installation

1. **System Preparation**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11+
sudo apt install python3.11 python3.11-venv python3.11-dev

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
```

2. **Application Setup**
```bash
# Create application user
sudo useradd -r -s /bin/false todo-mcp
sudo mkdir -p /opt/todo-mcp
sudo chown todo-mcp:todo-mcp /opt/todo-mcp

# Deploy application
sudo -u todo-mcp git clone <repository-url> /opt/todo-mcp
cd /opt/todo-mcp
sudo -u todo-mcp uv sync --frozen
```

3. **Production Configuration**
```bash
# Create production config
sudo -u todo-mcp cat > /opt/todo-mcp/.env << EOF
TODO_MCP_ENVIRONMENT=production
TODO_MCP_DATA_DIRECTORY=/var/lib/todo-mcp/data
TODO_MCP_LOG_LEVEL=INFO
TODO_MCP_LOG_FILE=/var/log/todo-mcp/server.log
TODO_MCP_BACKUP_ENABLED=true
TODO_MCP_BACKUP_DIRECTORY=/var/lib/todo-mcp/backups
TODO_MCP_MAX_CACHE_SIZE=5000
TODO_MCP_PERFORMANCE_MONITORING=true
EOF

# Create directories
sudo mkdir -p /var/lib/todo-mcp/{data,backups}
sudo mkdir -p /var/log/todo-mcp
sudo chown -R todo-mcp:todo-mcp /var/lib/todo-mcp /var/log/todo-mcp
```

4. **Systemd Service**
```bash
# Create systemd service
sudo cat > /etc/systemd/system/todo-mcp.service << EOF
[Unit]
Description=Todo MCP Server
After=network.target
Wants=network.target

[Service]
Type=simple
User=todo-mcp
Group=todo-mcp
WorkingDirectory=/opt/todo-mcp
Environment=PATH=/opt/todo-mcp/.venv/bin
ExecStart=/opt/todo-mcp/.venv/bin/python -m todo_mcp
ExecReload=/bin/kill -HUP \$MAINPID
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/lib/todo-mcp /var/log/todo-mcp

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable todo-mcp
sudo systemctl start todo-mcp
```

### Log Rotation

```bash
# Configure logrotate
sudo cat > /etc/logrotate.d/todo-mcp << EOF
/var/log/todo-mcp/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 todo-mcp todo-mcp
    postrotate
        systemctl reload todo-mcp
    endscript
}
EOF
```

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV TODO_MCP_ENVIRONMENT=production

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Create app user
RUN useradd -r -s /bin/false -m todo-mcp

# Set working directory
WORKDIR /app

# Copy application files
COPY --chown=todo-mcp:todo-mcp . .

# Install dependencies
RUN uv sync --frozen

# Create data directories
RUN mkdir -p /app/data /app/backups && \
    chown -R todo-mcp:todo-mcp /app

# Switch to app user
USER todo-mcp

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Expose port
EXPOSE 8000

# Start server
CMD ["uv", "run", "todo-mcp-server", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  todo-mcp:
    build: .
    container_name: todo-mcp-server
    restart: unless-stopped
    ports:
      - "8000:8000"
    volumes:
      - todo_data:/app/data
      - todo_backups:/app/backups
      - todo_logs:/app/logs
    environment:
      - TODO_MCP_ENVIRONMENT=production
      - TODO_MCP_DATA_DIRECTORY=/app/data
      - TODO_MCP_BACKUP_DIRECTORY=/app/backups
      - TODO_MCP_LOG_FILE=/app/logs/server.log
      - TODO_MCP_MAX_CACHE_SIZE=5000
      - TODO_MCP_PERFORMANCE_MONITORING=true
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

volumes:
  todo_data:
  todo_backups:
  todo_logs:
```

### Docker Deployment Commands

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f todo-mcp

# Scale service
docker-compose up -d --scale todo-mcp=3

# Update deployment
docker-compose pull
docker-compose up -d
```

## Cloud Deployment

### AWS Deployment

#### Using ECS Fargate

1. **Create Task Definition**
```json
{
  "family": "todo-mcp-server",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "todo-mcp",
      "image": "your-account.dkr.ecr.region.amazonaws.com/todo-mcp:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "TODO_MCP_ENVIRONMENT",
          "value": "production"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/todo-mcp",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

2. **Deploy with Terraform**
```hcl
resource "aws_ecs_cluster" "todo_mcp" {
  name = "todo-mcp-cluster"
}

resource "aws_ecs_service" "todo_mcp" {
  name            = "todo-mcp-service"
  cluster         = aws_ecs_cluster.todo_mcp.id
  task_definition = aws_ecs_task_definition.todo_mcp.arn
  desired_count   = 2
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = var.private_subnet_ids
    security_groups = [aws_security_group.todo_mcp.id]
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.todo_mcp.arn
    container_name   = "todo-mcp"
    container_port   = 8000
  }
}
```

#### Using Lambda (Serverless)

```python
# lambda_handler.py
import json
import asyncio
from src.todo_mcp.server import TodoMCPServer
from src.todo_mcp.config import create_config

def lambda_handler(event, context):
    """AWS Lambda handler for Todo MCP Server."""
    
    # Initialize server
    config = create_config("production")
    server = TodoMCPServer(config)
    
    # Process MCP request
    try:
        # Extract MCP request from event
        mcp_request = json.loads(event['body'])
        
        # Process request
        result = asyncio.run(server.handle_request(mcp_request))
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(result)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```

### Google Cloud Platform

#### Using Cloud Run

```yaml
# cloudbuild.yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/todo-mcp:$COMMIT_SHA', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/todo-mcp:$COMMIT_SHA']
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'todo-mcp-server'
      - '--image=gcr.io/$PROJECT_ID/todo-mcp:$COMMIT_SHA'
      - '--region=us-central1'
      - '--platform=managed'
      - '--allow-unauthenticated'
```

#### Deployment Commands

```bash
# Deploy to Cloud Run
gcloud run deploy todo-mcp-server \
  --image gcr.io/PROJECT_ID/todo-mcp:latest \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars TODO_MCP_ENVIRONMENT=production
```

### Azure Deployment

#### Using Container Instances

```bash
# Create resource group
az group create --name todo-mcp-rg --location eastus

# Deploy container
az container create \
  --resource-group todo-mcp-rg \
  --name todo-mcp-server \
  --image your-registry/todo-mcp:latest \
  --dns-name-label todo-mcp-unique \
  --ports 8000 \
  --environment-variables \
    TODO_MCP_ENVIRONMENT=production \
    TODO_MCP_LOG_LEVEL=INFO
```

## Monitoring & Maintenance

### Health Checks

```bash
# Basic health check
curl -f http://localhost:8000/health || exit 1

# Detailed status check
curl http://localhost:8000/status
```

### Monitoring Setup

#### Prometheus Metrics

```python
# Add to server.py
from prometheus_client import Counter, Histogram, generate_latest

# Metrics
REQUEST_COUNT = Counter('todo_mcp_requests_total', 'Total requests', ['tool', 'status'])
REQUEST_DURATION = Histogram('todo_mcp_request_duration_seconds', 'Request duration', ['tool'])

@app.route('/metrics')
def metrics():
    return generate_latest()
```

#### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "Todo MCP Server",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(todo_mcp_requests_total[5m])"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph", 
        "targets": [
          {
            "expr": "histogram_quantile(0.95, todo_mcp_request_duration_seconds_bucket)"
          }
        ]
      }
    ]
  }
}
```

### Backup Strategy

```bash
#!/bin/bash
# backup.sh - Automated backup script

BACKUP_DIR="/var/backups/todo-mcp"
DATA_DIR="/var/lib/todo-mcp/data"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup
mkdir -p "$BACKUP_DIR/$DATE"
cp -r "$DATA_DIR" "$BACKUP_DIR/$DATE/"

# Compress backup
tar -czf "$BACKUP_DIR/todo-mcp-$DATE.tar.gz" -C "$BACKUP_DIR" "$DATE"
rm -rf "$BACKUP_DIR/$DATE"

# Cleanup old backups (keep 30 days)
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete

# Upload to S3 (optional)
aws s3 cp "$BACKUP_DIR/todo-mcp-$DATE.tar.gz" s3://your-backup-bucket/
```

### Log Management

```bash
# Centralized logging with rsyslog
echo "*.* @@log-server:514" >> /etc/rsyslog.conf

# ELK Stack integration
filebeat.inputs:
- type: log
  paths:
    - /var/log/todo-mcp/*.log
  fields:
    service: todo-mcp
```

## Security Considerations

### Network Security

```bash
# Firewall configuration
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 8000/tcp  # Application
sudo ufw enable

# Nginx reverse proxy with SSL
server {
    listen 443 ssl http2;
    server_name todo-mcp.example.com;
    
    ssl_certificate /etc/letsencrypt/live/todo-mcp.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/todo-mcp.example.com/privkey.pem;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Application Security

1. **Environment Variables**
```bash
# Use secrets management
export TODO_MCP_SECRET_KEY=$(aws secretsmanager get-secret-value --secret-id todo-mcp-key --query SecretString --output text)
```

2. **File Permissions**
```bash
# Secure file permissions
chmod 600 /opt/todo-mcp/.env
chmod 755 /var/lib/todo-mcp
chmod 644 /var/lib/todo-mcp/data/*
```

3. **Regular Updates**
```bash
# Automated security updates
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

### Compliance

- **Data Encryption**: Enable encryption at rest and in transit
- **Audit Logging**: Log all administrative actions
- **Access Control**: Implement role-based access control
- **Data Retention**: Configure automatic data purging
- **Backup Encryption**: Encrypt all backup files

## Troubleshooting

### Common Issues

1. **Service Won't Start**
```bash
# Check logs
journalctl -u todo-mcp -f

# Check configuration
uv run todo-mcp-server validate

# Test configuration
uv run todo-mcp-server --test-config
```

2. **Performance Issues**
```bash
# Monitor resources
htop
iotop

# Check cache performance
curl http://localhost:8000/cache-stats

# Run performance tests
uv run pytest tests/test_integration/test_performance_load.py
```

3. **Storage Issues**
```bash
# Check disk space
df -h

# Check file permissions
ls -la /var/lib/todo-mcp/

# Repair corrupted files
uv run python -c "from src.todo_mcp.storage.file_manager import FileManager; FileManager('/var/lib/todo-mcp/data').repair_corrupted_files()"
```

### Emergency Procedures

1. **Service Recovery**
```bash
# Stop service
sudo systemctl stop todo-mcp

# Restore from backup
sudo -u todo-mcp tar -xzf /var/backups/todo-mcp/latest.tar.gz -C /var/lib/todo-mcp/

# Start service
sudo systemctl start todo-mcp
```

2. **Data Recovery**
```bash
# Restore specific task
sudo -u todo-mcp cp /var/backups/todo-mcp/data/tasks/task-001.md /var/lib/todo-mcp/data/tasks/

# Rebuild indexes
uv run python -c "from src.todo_mcp.services.task_service import TaskService; TaskService().rebuild_indexes()"
```

This deployment guide provides comprehensive instructions for deploying the Todo MCP Server in various environments. Choose the deployment method that best fits your infrastructure and requirements.