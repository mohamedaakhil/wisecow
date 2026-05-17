# 🐄 Wisecow – Containerised & Deployed on Kubernetes

[![CI/CD](https://github.com/mohamedaakhil/wisecow/actions/workflows/ci-cd.yaml/badge.svg)](https://github.com/mohamedaakhil/wisecow/actions)

Wisecow is a shell-based web server that serves random cow wisdom using `fortune` + `cowsay`.  
This repository contains everything needed to **build, containerise, deploy, and secure** it on Kubernetes with a full CI/CD pipeline.

---

## 📁 Repository Structure

```
wisecow/
├── wisecow.sh                   # Application source (supports TLS via socat)
├── Dockerfile                   # Docker image definition
├── k8s/
│   ├── namespace.yaml           # wisecow namespace
│   ├── deployment.yaml          # Deployment (2 replicas, rolling update)
│   ├── service.yaml             # LoadBalancer / NodePort service
│   ├── ingress.yaml             # NGINX Ingress with TLS termination
│   └── cluster-issuer.yaml      # cert-manager ClusterIssuer (Let's Encrypt)
├── tls/
│   └── generate-tls-secret.sh  # Helper: self-signed cert for local dev
└── .github/workflows/
    └── ci-cd.yaml               # GitHub Actions – build → push → deploy
```

---

## 🚀 Quick Start (Local – Minikube / Kind)

### 1. Prerequisites

```bash
# Minikube
minikube start --driver=docker
minikube addons enable ingress

# Or Kind
kind create cluster --name wisecow
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
```

### 2. Build & load the image locally

```bash
docker build -t wisecow:local .

# Minikube
minikube image load wisecow:local

# Kind
kind load docker-image wisecow:local --name wisecow
```

### 3. Deploy

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

### 4. Access

```bash
# Minikube
minikube service wisecow-service -n wisecow

# Kind – port-forward
kubectl port-forward svc/wisecow-service 4499:80 -n wisecow
# then open http://localhost:4499
```

---

## 🔒 TLS Setup

### Production – cert-manager + Let's Encrypt

```bash
# 1. Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/latest/download/cert-manager.yaml

# 2. Create ClusterIssuer (edit your email in cluster-issuer.yaml first)
kubectl apply -f k8s/cluster-issuer.yaml

# 3. Apply ingress (edit wisecow.example.com to your domain first)
kubectl apply -f k8s/ingress.yaml
```

### Local Development – Self-signed Certificate

```bash
bash tls/generate-tls-secret.sh wisecow.local
echo "$(minikube ip)  wisecow.local" | sudo tee -a /etc/hosts
```

---

## ⚙️ CI/CD Pipeline (GitHub Actions)

| Step | Description |
|------|-------------|
| **Checkout** | Fetches the repository |
| **Buildx setup** | Enables multi-platform builds |
| **GHCR login** | Authenticates with GITHUB_TOKEN |
| **Build & Push** | Pushes to `ghcr.io/mohamedaakhil/wisecow` |
| **Deploy** | Patches Deployment image, applies manifests, waits for rollout |

### Required GitHub Secret

| Secret | How to get it |
|--------|---------------|
| `KUBE_CONFIG` | Run `base64 -w 0 ~/.kube/config` and paste the output |

Add it at: `https://github.com/mohamedaakhil/wisecow/settings/secrets/actions`

---

## 📦 Push to GitHub

```bash
git init
git add .
git commit -m "Initial wisecow containerisation and k8s deployment"
git branch -M main
git remote add origin https://github.com/mohamedaakhil/wisecow.git
git push -u origin main
```

---

## 🛠️ Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `PORT` | `4499` | Listening port |
| `TLS_CERT` | `/certs/tls.crt` | Path to TLS certificate |
| `TLS_KEY` | `/certs/tls.key` | Path to TLS private key |

---

## 📝 License

Apache-2.0
