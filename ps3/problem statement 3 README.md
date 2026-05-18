# PS3 – Zero-Trust KubeArmor Policy for Wisecow

## What is wisecow?

Wisecow is a **bash shell web server** (`wisecow.sh`) that:
- Listens on port **4499** using `nc` (plain HTTP) or `socat` (TLS)
- Calls `fortune` to generate a random wisdom quote
- Pipes it through `cowsay` and returns HTML
- Runs on `ubuntu:22.04` base image

This workload context is critical – the allowlist is built around exactly the binaries wisecow.sh actually uses.

---

## Policy Architecture

| # | Policy Name | Action | Protects Against |
|---|-------------|--------|-----------------|
| 1 | `zt-wisecow-allow-process-whitelist` | **Allow** → least-permissive | Any binary not in: bash, nc, socat, cowsay, fortune, cat, sleep, rm, mkfifo |
| 2 | `zt-wisecow-block-sa-token` | Block | K8s API lateral movement via service-account token |
| 3 | `zt-wisecow-block-pkg-managers` | Block | apt, curl, wget, python (runtime supply-chain attacks) |
| 4 | `zt-wisecow-protect-system-dirs` | Block | Writes to /bin, /etc, /lib, /usr (OS file-integrity) |
| 5 | `zt-wisecow-block-history-tamper` | Block | .bash_history deletion (anti-forensics) |
| 6 | `zt-wisecow-block-raw-sockets` | Block | Raw socket creation (ARP spoofing, port scanning) |
| 7 | `zt-wisecow-audit-tls-certs` | Audit | Unexpected reads of /certs/ (logged, not blocked) |

> **Key principle:** Policy 1 uses `action: Allow`. KubeArmor automatically enters **least-permissive (deny-all) mode** once any Allow policy exists. Every binary not listed is implicitly blocked — no separate Block rule needed for them.

---

## Step 1 – Install KubeArmor

```bash
# Via Helm (recommended)
helm repo add kubearmor https://kubearmor.github.io/charts
helm repo update
helm upgrade --install kubearmor kubearmor/kubearmor \
  --namespace kubearmor --create-namespace

# Verify
kubectl get pods -n kubearmor
# All kubearmor-* pods should be Running
```

---

## Step 2 – Install karmor CLI

```bash
curl -sfL https://raw.githubusercontent.com/kubearmor/kubearmor-client/main/install.sh \
  | sudo sh -s -- -b /usr/local/bin

karmor version
```

---

## Step 3 – Ensure wisecow is running in the wisecow namespace

```bash
kubectl get pods -n wisecow -l app=wisecow
# Should show Running pod(s)
```

If not yet deployed:
```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

---

## Step 4 – Apply the Zero-Trust Policy Suite

```bash
kubectl apply -f kubearmor-zero-trust-policy.yaml

# Confirm all 7 policies created
kubectl get kubearmorpolicies -n wisecow
```

Expected output:
```
NAME                                  AGE
zt-wisecow-allow-process-whitelist    5s
zt-wisecow-audit-tls-certs            5s
zt-wisecow-block-history-tamper       5s
zt-wisecow-block-pkg-managers         5s
zt-wisecow-block-raw-sockets          5s
zt-wisecow-block-sa-token             5s
zt-wisecow-protect-system-dirs        5s
```

---

## Step 5 – Trigger Violations (for Screenshot)

```bash
# Get the pod name
POD=$(kubectl get pod -n wisecow -l app=wisecow -o jsonpath='{.items[0].metadata.name}')

# Shell into the pod
kubectl exec -it $POD -n wisecow -- /bin/bash
```

**Inside the pod – try these (all should show Permission denied):**

```bash
# VIOLATION 1: Package manager (Policy 3)
apt-get update
# → bash: /usr/bin/apt-get: Permission denied

# VIOLATION 2: Download tool (Policy 3)
curl https://example.com
# → bash: /usr/bin/curl: Permission denied

# VIOLATION 3: Read the K8s service account token (Policy 2)
cat /run/secrets/kubernetes.io/serviceaccount/token
# → cat: /run/secrets/kubernetes.io/serviceaccount/token: Permission denied

# VIOLATION 4: Write to /etc (Policy 4)
touch /etc/malicious
# → touch: cannot touch '/etc/malicious': Permission denied

# VIOLATION 5: Run an unlisted binary (Policy 1 – least-permissive)
whoami
# → bash: /usr/bin/whoami: Permission denied

# VIOLATION 6: Try to run a new shell (Policy 1)
/bin/sh -c "id"
# → bash: /bin/sh: Permission denied  (sh is not in the allowlist)
```

---

## Step 6 – View Violation Logs

**Option A – karmor logs (real-time, best for screenshots):**
```bash
# Run this in a separate terminal BEFORE triggering violations
karmor logs --logFilter=policy -n wisecow
```

Sample output:
```json
{
  "Timestamp": 1716000000,
  "NamespaceName": "wisecow",
  "PodName": "wisecow-deployment-xxxxxxx",
  "Labels": "app=wisecow",
  "ProcessName": "/usr/bin/apt-get",
  "PolicyName": "zt-wisecow-block-pkg-managers",
  "Severity": "9",
  "Action": "Block",
  "Result": "Permission denied",
  "Message": "ZT VIOLATION: Package manager / download tool execution blocked"
}
```

**Option B – kubectl logs on the KubeArmor daemonset pod:**
```bash
NGINX_NODE=$(kubectl get pod -n wisecow -l app=wisecow \
  -o jsonpath='{.items[0].spec.nodeName}')
KA_POD=$(kubectl get pod -n kubearmor -l app=kubearmor \
  -o jsonpath="{.items[?(@.spec.nodeName=='$NGINX_NODE')].metadata.name}")
kubectl logs -n kubearmor $KA_POD | grep "zt-wisecow" | tail -20
```

---

## Step 7 – Screenshot Checklist

Take and save screenshots showing:

1. `kubectl get kubearmorpolicies -n wisecow` (all 7 policies listed)
2. Terminal showing `Permission denied` when running `apt-get` or `curl` inside the pod
3. `karmor logs` output with `"Action": "Block"` and the policy name visible
4. `kubectl get pods -n kubearmor` (KubeArmor running)

---

## Step 8 – Commit to Your Forked Repo

```bash
mkdir -p ps3
cp kubearmor-zero-trust-policy.yaml ps3/
cp violation-screenshot.png ps3/   # rename to match your actual screenshot

git add ps3/
git commit -m "PS3: Add KubeArmor zero-trust policy for wisecow + violation screenshot"
git push origin main
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Binaries still run despite Allow policy | Default posture may still be `audit`. Run: `kubectl annotate ns wisecow kubearmor-file-posture=block --overwrite` |
| `kubectl apply` fails with "no matches for kind" | KubeArmor CRDs not installed. Apply KubeArmor first (Step 1). |
| `karmor` command not found | Re-run the install script or use `kubectl logs` on the KubeArmor pod instead. |
| wisecow itself breaks after applying policies | The allowlist includes all binaries wisecow.sh uses. If a binary is missing (path differs), check with `which <binary>` inside the pod and add it to Policy 1. |

---

## References

- KubeArmor docs: https://docs.kubearmor.io/kubearmor/
- Policy examples: https://docs.kubearmor.io/kubearmor/documentation/security_policy_examples
- Getting started: https://docs.kubearmor.io/kubearmor/quick-links/deployment_guide
- wisecow repo: https://github.com/mohamedaakhil/wisecow
