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

## 🚀 Quick Start (Local – Minikube + VirtualBox)

### 1. Prerequisites

- Install [VirtualBox](https://www.virtualbox.org/wiki/Downloads) — click **Windows hosts**
- Install [Minikube](https://minikube.sigs.k8s.io/docs/start/)
- Install [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl-windows/)

### 2. Start Minikube

```bash
minikube start --driver=virtualbox
minikube status
```

### 3. Deploy

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

### 4. Check pods are running

```bash
kubectl get pods -n wisecow
# Wait until STATUS shows Running and READY shows 1/1
```

### 5. Open the app in browser

```bash
minikube service wisecow-service -n wisecow
# Automatically opens browser with the wisecow app
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
# Add to hosts file (PowerShell as Admin on Windows)
Add-Content -Path "C:\Windows\System32\drivers\etc\hosts" -Value "$(minikube ip)  wisecow.local"
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
| `KUBE_CONFIG` | Run the command below in PowerShell and paste the output |

```powershell
# Windows PowerShell — copies base64 kubeconfig to clipboard
[Convert]::ToBase64String([IO.File]::ReadAllBytes("$HOME\.kube\config")) | Set-Clipboard
```

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
