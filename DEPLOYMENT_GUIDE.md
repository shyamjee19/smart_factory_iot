# Deployment Guide

This guide describes how to deploy the Smart Factory IoT Platform.

## Prerequisites
- Docker and Docker Compose
- Kubernetes Cluster (Minikube, EKS, GKE, AKS)
- `kubectl` configured

## Local Deployment (Docker Compose)
For local development and testing, use the provided Docker Compose files.

1. Ensure you have the `.env` file configured.
2. Build and start the services:
   ```bash
   docker-compose build
   docker-compose up -d
   ```
3. To stop the services:
   ```bash
   docker-compose down
   ```

## Production Deployment (Kubernetes)
The project includes Kubernetes manifests for deploying the application to a cluster.

1. Apply Secrets and ConfigMaps:
   ```bash
   kubectl apply -f k8s/config.yaml
   ```
2. Deploy PostgreSQL:
   ```bash
   kubectl apply -f k8s/postgres-deployment.yaml
   ```
3. Deploy Backend API:
   ```bash
   kubectl apply -f k8s/backend-deployment.yaml
   ```
4. Deploy Frontend Dashboard:
   ```bash
   kubectl apply -f k8s/frontend-deployment.yaml
   ```
5. Verify Deployment:
   ```bash
   kubectl get pods
   kubectl get services
   ```

## CI/CD Pipeline
The project uses GitHub Actions for CI/CD. The pipeline is defined in `.github/workflows/main.yml`.

- **Test**: Runs Python unit tests using `pytest`.
- **Build-and-Push**: Builds Docker images and pushes them to Docker Hub on merge to `main`.
