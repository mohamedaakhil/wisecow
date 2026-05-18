# KubeArmor Zero-Trust Policy – Setup & Violation Guide

## 1. Install KubeArmor on Minikube

```powershell
# Install karmor CLI (Windows PowerShell)
curl.exe -sfL https://raw.githubusercontent.com/kubearmor/kubearmor-client/main/install.sh | powershell

# Or install via Helm
helm repo add kubearmor https://kubearmor.github.io/charts
helm repo update
helm upgrade --install kubearmor kubearmor/kubearmor -n kube-system
```

## 2. Verify KubeArmor is running

```powershell
kubectl get pods -n kube-system | findstr kubearmor
```

## 3. Apply the zero-trust policies

```powershell
kubectl apply -f k8s/kubearmor/kubearmor-policy.yaml
```

## 4. Verify policies are applied

```powershell
kubectl get kubearmorpolicies -n wisecow
```

Expected output:
```
NAME                           AGE
wisecow-block-exec             10s
wisecow-block-sensitive-files  10s
wisecow-block-raw-network      10s
wisecow-file-integrity         10s
wisecow-audit-capabilities     10s
```

## 5. Trigger a policy violation (for screenshot)

```powershell
# Get the pod name
kubectl get pods -n wisecow

# Try to exec into the pod and run a blocked command
kubectl exec -it -n wisecow <POD_NAME> -- /bin/bash

# Inside the pod, try these blocked commands:
cat /etc/shadow        # blocked by wisecow-block-sensitive-files
wget google.com        # blocked by wisecow-block-exec
apt-get install curl   # blocked by wisecow-block-exec
```

## 6. View violation logs (take screenshot of this)

```powershell
# Using karmor CLI
karmor log --namespace wisecow

# Or using kubectl logs
kubectl logs -n kube-system -l app=kubearmor | findstr wisecow
```

## 7. What to screenshot
- The output of `kubectl get kubearmorpolicies -n wisecow`
- The violation log showing BLOCK action
- The terminal showing "Permission denied" when trying blocked commands
