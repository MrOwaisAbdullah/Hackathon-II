# External Services Setup Guide - TeamFlow Phase 5

**Purpose**: Step-by-step instructions for setting up all external services required for Phase 5 Advanced Cloud Deployment.

**Estimated Total Setup Time**: 2-3 hours (most services are free tier)

---

## Table of Contents

1. [Oracle Cloud OKE Setup](#1-oracle-cloud-oke-setup)
2. [Redpanda/Kafka Cluster Setup](#2-redpandakafka-cluster-setup)
3. [Email Service Provider Setup](#3-email-service-provider-setup)
4. [Container Registry Setup](#4-container-registry-setup)
5. [GitHub Secrets Configuration](#5-github-secrets-configuration)
6. [Domain and TLS Configuration](#6-domain-and-tls-configuration)
7. [Verification Checklist](#7-verification-checklist)

---

## 1. Oracle Cloud OKE Setup

**Purpose**: Provision Kubernetes cluster on Oracle OKE Always Free tier.

**Time Estimate**: 30-45 minutes

### 1.1 Create Oracle Cloud Account

1. Go to https://www.oracle.com/cloud/free/
2. Click "Try for Free"
3. Sign up with:
   - Email address
   - Full name
   - Country/region
   - Phone number (for verification)
4. Verify email address
5. Verify phone number (receive SMS code)
6. Create password
7. Select home region (recommend: `us-ashburn-1` for low latency)
8. Enter credit card (required for free tier, but not charged)
9. Complete account creation

**Verification**: Check email for "Oracle Cloud Free Tier Account Activated"

---

### 1.2 Install OCI CLI

**On Windows**:
```powershell
# Download installer from
# https://docs.oracle.com/en-us/iaas/Content/API/Concepts/cliconcepts.htm
# Run installer and follow prompts
```

**On Mac**:
```bash
brew install oci-cli
```

**On Linux**:
```bash
# Install from GitHub releases
curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh | bash
```

---

### 1.3 Configure OCI CLI

```bash
# Run configuration wizard
oci setup config

# Enter prompts:
# - Enter a location for your config [/home/user/.oci/config]: (press Enter for default)
# - Enter a user OCID: Get from https://console.oracle.com/identity/users
# - Enter a tenancy OCID: Get from https://console.oracle.com/tenancy
# - Enter a region (e.g. us-ashburn-1): us-ashburn-1
# - Do you want to generate a new API key pairing? [Y/n]: Y
# - Enter a directory for your keys to be created [/home/user/.oci]: (press Enter)
# - Enter a name for your key [oci_api_key]: (press Enter)
# - Enter a passphrase for your private key (empty for no passphrase): (press Enter)

# After setup, verify
oci iam compartment list
```

**Expected Output**: JSON list of compartments

---

### 1.4 Create Compartment

```bash
# Create compartment for TeamFlow resources
COMPARTMENT_NAME="TeamFlow"
TENANCY_OCID="ocid1.tenancy.oc1...aaaa..."  # Replace with your tenancy OCID

oci iam compartment create \
  --compartment-id $TENANCY_OCID \
  --name "$COMPARTMENT_NAME" \
  --description "TeamFlow project resources" \
  --freeform-tags '{"Project":"TeamFlow","Environment":"Production"}'

# Get compartment OCID
COMPARTMENT_OCID=$(oci iam compartment list \
  --compartment-id $TENANCY_OCID \
  --name "$COMPARTMENT_NAME" \
  --query "data[0].id" --raw-output)

echo "Compartment OCID: $COMPARTMENT_OCID"
```

**Verification**:
```bash
# Log in to Oracle Cloud Console
# Navigate to Identity & Security → Compartments
# Verify "TeamFlow" compartment exists
```

---

### 1.5 Generate API Key (if not generated during setup)

```bash
# Create API key directory
mkdir -p ~/.oci

# Generate private key
openssl genrsa -out ~/.oci/oci_api_key.pem 2048

# Set permissions
chmod go-rwx ~/.oci/oci_api_key.pem

# Generate public key
openssl rsa -pubout -in ~/.oci/oci_api_key.pem -out ~/.oci/oci_api_key_public.pem

# Display public key (copy this)
cat ~/.oci/oci_api_key_public.pem

# Add API key to Oracle Cloud Console
# Settings → API Keys → Add API Key → Paste public key
```

---

### 1.6 Create OKE Cluster

```bash
# Set variables
CLUSTER_NAME="teamflow-cluster"
REGION="us-ashburn-1"

# Create cluster
oci ce cluster create \
  --name "$CLUSTER_NAME" \
  --compartment-id "$COMPARTMENT_OCID" \
  --kubernetes-version 1.29 \
  --endpoint-type PUBLIC_ENDPOINT \
  --options file://cluster-options.json

# Create cluster-options.json file:
cat > cluster-options.json << 'EOF'
{
  "kubernetesNetworkConfig": {
    "podsCidr": "10.244.0.0/16",
    "servicesCidr": "10.96.0.0/16"
  },
  "serviceLbConfig": {
    "lbShape": "flexible",
    "lbMinBandwidth": 10,
    "lbMaxBandwidth": 10
  },
  "addons": [
    {
      "name": "KubernetesDashboard"
    }
  ]
}
EOF
```

**Time Estimate**: 10-15 minutes for cluster provisioning

---

### 1.7 Create Node Pool

```bash
# Wait for cluster to be ACTIVE (check in Console)
# Then create node pool

oci ce node-pool create \
  --cluster-id "$CLUSTER_ID" \
  --name "teamflow-node-pool" \
  --compartment-id "$COMPARTMENT_OCID" \
  --kubernetes-version 1.29 \
  --node-shape "VM.Standard.E4.Flex" \
  --node-config-json '{"ocpus": 1, "memory": 8}' \
  --quantity 1 \
  --ssh-public-key-file ~/.ssh/id_rsa.pub
```

**Note**: This creates 1 node with 1 OCPU and 8GB RAM (within Always Free limits).

---

### 1.8 Generate Kubeconfig

```bash
# Get cluster ID
CLUSTER_ID=$(oci ce cluster list \
  --compartment-id "$COMPARTMENT_OCID" \
  --name "$CLUSTER_NAME" \
  --query "data[0].id" --raw-output)

# Create kubeconfig
oci ce cluster create-kubeconfig \
  --cluster-id "$CLUSTER_ID" \
  --file $HOME/.kube/config-teamflow \
  --region "$REGION"

# Set KUBECONFIG
export KUBECONFIG=$HOME/.kube/config-teamflow

# Add to .bashrc for persistence
echo "export KUBECONFIG=$HOME/.kube/config-teamflow" >> ~/.bashrc

# Verify cluster access
kubectl get nodes
```

**Expected Output**:
```
NAME                               STATUS   ROLES   AGE   VERSION
teamflow-node-pool-1-...           Ready    <none>  5m    v1.29.0
```

---

### 1.9 Install Helm on OKE Cluster

```bash
# Download Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Verify
helm version
```

---

## 2. Redpanda/Kafka Cluster Setup

**Purpose**: Deploy Redpanda Kafka cluster to OKE for event streaming.

**Time Estimate**: 15-20 minutes

### 2.1 Add Redpanda Helm Repository

```bash
helm repo add redpanda https://charts.redpanda.com
helm repo update
```

---

### 2.2 Create Kafka Namespace

```bash
kubectl create namespace kafka
```

---

### 2.3 Deploy Redpanda

```bash
# Deploy Redpanda with resource limits for Always Free tier
helm install redpanda redpanda/redpanda \
  --namespace kafka \
  --set replicas=1 \
  --set resources.limits.memory=2Gi \
  --set resources.requests.memory=256Mi \
  --set resources.limits.cpu=1 \
  --set resources.requests.cpu=100m \
  --set storage.persistence.size=10Gi \
  --set configuration.redpanda.developer_mode=true

# Wait for Redpanda to be ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=redpanda -n kafka --timeout=300s
```

---

### 2.4 Create Kafka Topics

```bash
# Access Redpanda pod
kubectl exec -it redpanda-0 -n kafka -- bash

# Inside Redpanda pod, create topics
rpk topic create task-events --partitions 3 --replication-factor 1
rpk topic create reminders --partitions 3 --replication-factor 1
rpk topic create time-logged --partitions 1 --replication-factor 1
rpk topic create task-updates --partitions 3 --replication-factor 1

# Verify topics
rpk topic list

# Expected output:
# NAME            PARTITIONS  REPLICAS
# task-events     3           1
# reminders       3           1
# time-logged     1           1
# task-updates    3           1

# Exit pod
exit
```

---

### 2.5 Verify Redpanda Connectivity

```bash
# Port-forward Redpanda admin UI
kubectl port-forward svc/redpanda -n kafka 8080:8080

# Open http://localhost:8080 in browser
# Should show Redpanda Console
```

---

## 3. Email Service Provider Setup

**Purpose**: Configure transactional email service for reminder notifications.

**Time Estimate**: 10-15 minutes

### 3.1 Create SendGrid Account

1. Go to https://signup.sendgrid.com/
2. Sign up with:
   - Email address
   - Username
   - Password
3. Verify email address
4. Complete account setup

**Free Tier**: 100 emails/day forever (no credit card required)

---

### 3.2 Generate API Key

```bash
# Log in to SendGrid Console
# https://app.sendgrid.com/

# Navigate to Settings → API Keys
# Click "Create API Key"
# Name: "TeamFlow Production"
# Permissions: Mail Send > Full Access
# Click "Create & View"
# Copy API key (shown only once!)
```

**Example API Key**:
```
SG.your_api_key_here.abc123def456...
```

---

### 3.3 Verify Email Domain (Recommended)

```bash
# In SendGrid Console, go to Settings → Sender Authentication
# Click "Authenticate Your Domain"
# Enter your domain (e.g., teamflow.example.com)
# Add DNS records to your domain registrar:
#   CNAME: smtp._domainkey.teamflow.example.com → ...sendgrid.net
#   TXT: @ → v=spf1 include:sendgrid.net -all

# Wait for DNS propagation (5-30 minutes)
# Click "Verify" in SendGrid Console
```

**Alternative**: Use single sender verification (Settings → Single Sender Verification) if you don't have a domain.

---

### 3.4 Send Test Email

```bash
# Use curl to test SendGrid API
curl -X "POST" "https://api.sendgrid.com/v3/mail/send" \
  --header "Authorization: Bearer SG.YOUR_API_KEY" \
  --header "Content-Type: application/json" \
  --data '{
    "personalizations": [{"to": [{"email": "your@email.com"}]}],
    "from": {"email": "noreply@teamflow.example.com"},
    "subject": "SendGrid Test",
    "content": [{"type": "text/plain", "value": "Hello from SendGrid!"}]
  }'

# Expected: 202 Accepted
# Check your email inbox
```

---

## 4. Container Registry Setup

**Purpose**: Store and distribute container images for deployment.

**Time Estimate**: 5-10 minutes

### 4.1 Create GitHub Container Registry (Recommended)

**Why GHCR**: Free unlimited private repos, integrates with GitHub Actions.

```bash
# GitHub Container Registry is automatically available
# No setup required!

# Just need a GitHub personal access token (PAT) with write:packages scope
```

---

### 4.2 Generate GitHub Personal Access Token

```bash
# Log in to GitHub
# Settings → Developer settings → Personal access tokens → Tokens (classic)
# Click "Generate new token (classic)"

# Token settings:
# - Note: "TeamFlow Container Registry"
# - Expiration: 90 days (or no expiration)
# - Scopes:
#   ✅ write:packages
#   ✅ read:packages
#   ✅ repo (full control of private repositories)

# Click "Generate token"
# Copy token (shown only once!)
```

**Example Token**:
```
ghp_your_token_here.abc123def456...
```

---

### 4.3 Login to GHCR

```bash
# Login using GitHub token
echo $GITHUB_TOKEN | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin

# Or use GitHub CLI
gh auth login
gh auth token

# Verify login
docker pull ghcr.io/YOUR_GITHUB_USERNAME/teamflow-backend:latest
```

---

### 4.4 Alternative: Oracle Container Registry (OCIR)

```bash
# If using OKE, OCIR is already available
# Get OCIR endpoint
oci artifacts container repository list --compartment-id $COMPARTMENT_OCID

# Example: ocir.com/tenancy-name/...

# Create auth token in OCI Console
# User Settings → Auth Tokens → Create Token
# Copy token (shown only once!)

# Login to OCIR
docker login ocir.com
# Username: tenancy-name/username
# Password: auth token
```

---

## 5. GitHub Secrets Configuration

**Purpose**: Securely store sensitive configuration for CI/CD pipeline.

**Time Estimate**: 5-10 minutes

### 5.1 Add Secrets to GitHub Repository

```bash
# Navigate to repository on GitHub
# https://github.com/YOUR_USERNAME/teamflow

# Settings → Secrets and variables → Actions → New repository secret
```

**Required Secrets**:

| Secret Name | Value | Description |
|--------------|-------|-------------|
| `KUBE_CONFIG` | Base64-encoded kubeconfig file | OKE cluster credentials |
| `OCI_API_KEY` | Oracle Cloud API key | Cluster management (optional) |
| `SENDGRID_API_KEY` | SendGrid API key | Email sending |
| `DATABASE_URL` | Neon PostgreSQL connection string | Database connection |
| `OPENAI_API_KEY` | OpenAI API key | AI features (from Phase III) |
| `BETTER_AUTH_SECRET` | Better Auth secret key | Authentication |
| `GHCR_TOKEN` | GitHub PAT with write:packages | Container registry push |

---

### 5.2 Encode Kubeconfig

```bash
# Get kubeconfig file
export KUBECONFIG=$HOME/.kube/config-teamflow

# Encode to base64
cat $KUBECONFIG | base64 -w 0

# Copy the output
# Add to GitHub Secrets as KUBE_CONFIG
```

---

### 5.3 Add Secrets via GitHub CLI

```bash
# Install GitHub CLI
# https://cli.github.com/

# Login
gh auth login

# Add secrets
gh secret set KUBE_CONFIG -bteamflow < kubeconfig.base64
gh secret set SENDGRID_API_KEY -bteamflow <<< "SG.your_api_key"
gh secret set DATABASE_URL -bteamflow <<< "postgresql://..."
gh secret set OPENAI_API_KEY -bteamflow <<< "sk-..."
gh secret set BETTER_AUTH_SECRET -bteamflow <<< "your-secret-here"
gh secret set GHCR_TOKEN -bteamflow <<< "ghp_your_token"

# Verify
gh secret list -R teamflow-web
```

---

## 6. Domain and TLS Configuration

**Purpose**: Configure custom domain and SSL certificates for production deployment.

**Time Estimate**: 15-30 minutes (if using custom domain)

### 6.1 Purchase Custom Domain (Optional)

```bash
# Purchase domain from:
# - Namecheap: https://www.namecheap.com/
# - GoDaddy: https://www.godaddy.com/
# - Google Domains: https://domains.google.com/

# Example: teamflow.example.com
```

---

### 6.2 Configure DNS

```bash
# Add DNS records to point to OKE load balancer

# Get OKE load balancer IP
kubectl get svc teamflow-ingress -n teamflow

# Example output: 129.213.123.45

# Add A record in DNS provider:
# @ → 129.213.123.45
# www → 129.213.123.45
```

---

### 6.3 Configure TLS with Let's Encrypt (Free SSL)

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create ClusterIssuer
cat > letsencrypt-prod.yaml << 'EOF'
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your@email.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF

kubectl apply -f letsencrypt-prod.yaml

# Update Ingress to use TLS
# Add annotations:
# cert-manager.io/cluster-issuer: "letsencrypt-prod"
```

---

### 6.4 Alternative: Use OKE Load Balancer IP (No Custom Domain)

```bash
# If not using custom domain, use OKE load balancer IP directly
export LB_IP=$(kubectl get svc teamflow-ingress -n teamflow -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

echo "TeamFlow deployed at: http://$LB_IP"
```

---

## 7. Verification Checklist

### 7.1 Oracle Cloud OKE

- [ ] Oracle Cloud account created and verified
- [ ] Compartment "TeamFlow" exists
- [ ] OKE cluster "teamflow-cluster" is ACTIVE
- [ ] Node pool is ACTIVE with 1 node running
- [ ] kubectl can access cluster (`kubectl get nodes` works)
- [ ] Helm is installed on local machine

**Verification Commands**:
```bash
export KUBECONFIG=$HOME/.kube/config-teamflow
kubectl get nodes
# Expected: 1 node with Ready status

helm version
# Expected: version v3.x.x
```

---

### 7.2 Redpanda/Kafka

- [ ] Redpanda deployed to OKE cluster
- [ ] Redpanda pod is Running
- [ ] Kafka topics created (task-events, reminders, time-logged, task-updates)
- [ ] Redpanda Console accessible at http://localhost:8080

**Verification Commands**:
```bash
kubectl get pods -n kafka
# Expected: redpanda-0 Running

kubectl exec -it redpanda-0 -n kafka -- rpk topic list
# Expected: 4 topics listed
```

---

### 7.3 Email Service

- [ ] SendGrid account created
- [ ] API key generated
- [ ] Domain verified or single sender verified
- [ ] Test email sent successfully
- [ ] SENDGRID_API_KEY added to GitHub Secrets

**Verification Commands**:
```bash
# Send test email via curl (see Section 3.4)
# Check email inbox for test message
```

---

### 7.4 Container Registry

- [ ] GitHub Personal Access Token created with write:packages scope
- [ ] Docker login to ghcr.io successful
- [ ] GHCR_TOKEN added to GitHub Secrets

**Verification Commands**:
```bash
echo $GITHUB_TOKEN | docker login ghcr.io -u YOUR_USERNAME --password-stdin
# Expected: Login Succeeded

docker pull ghcr.io/YOUR_USERNAME/teamflow-backend:latest
# Expected: Image pulled or "manifest not found" (OK if image doesn't exist yet)
```

---

### 7.5 GitHub Secrets

- [ ] All required secrets added to GitHub repository
- [ ] KUBE_CONFIG is base64-encoded
- [ ] Secrets do not contain plaintext values

**Verification Commands**:
```bash
gh secret list -R teamflow-web
# Expected: List of 7 secrets (see Section 5.1)
```

---

### 7.6 Domain and TLS

- [ ] (Optional) Custom domain purchased
- [ ] (Optional) DNS A record points to OKE load balancer IP
- [ ] (Optional) TLS certificate issued by Let's Encrypt
- [ ] Application accessible via domain or load balancer IP

**Verification Commands**:
```bash
# Get load balancer IP
kubectl get svc teamflow-ingress -n teamflow
# Test access
curl http://$LB_IP
# Expected: HTML response from frontend
```

---

## 8. Troubleshooting

### 8.1 OKE Cluster Creation Fails

**Error**: "Insufficient quota for Always Free tier"

**Solution**:
- Check if you have existing Always Free resources
- Verify region supports Always Free (us-ashburn-1, us-phoenix-1, eu-frankfurt-1, etc.)
- Try different region

---

### 8.2 Kubectl Cannot Access Cluster

**Error**: "The connection to the server localhost:8080 was refused"

**Solution**:
```bash
# Verify KUBECONFIG is set
echo $KUBECONFIG

# If empty, set KUBECONFIG
export KUBECONFIG=$HOME/.kube/config-teamflow

# Test again
kubectl get nodes
```

---

### 8.3 Redpanda Pod Pending

**Error**: Redpanda pod stuck in Pending state

**Solution**:
```bash
# Describe pod for error details
kubectl describe pod redpanda-0 -n kafka

# Check if storage class exists
kubectl get storageclass

# If no default storage class, create one
# Or specify storage class in Helm values
```

---

### 8.4 SendGrid API Fails

**Error**: "401 Unauthorized" from SendGrid API

**Solution**:
```bash
# Verify API key is correct
# Check API key permissions (Mail Send > Full Access)

# Regenerate API key if needed
# SendGrid Console → Settings → API Keys → Edit → Regenerate
```

---

### 8.5 GitHub Actions Pipeline Fails

**Error**: "Failed to pull image from ghcr.io"

**Solution**:
```bash
# Verify GHCR_TOKEN has correct permissions
# Check token has write:packages scope

# Test login manually
echo $GITHUB_TOKEN | docker login ghcr.io -u YOUR_USERNAME --password-stdin

# If fails, regenerate token and update GitHub Secret
```

---

## 9. Cost Estimate

**All Services (Monthly Cost)**:

| Service | Tier | Cost |
|---------|------|------|
| **Oracle OKE** | Always Free | $0 |
| **Redpanda** | Self-hosted on OKE | $0 |
| **SendGrid** | Free (100 emails/day) | $0 |
| **GitHub Container Registry** | Free unlimited private repos | $0 |
| **GitHub Actions** | Free (2000 minutes/month) | $0 |
| **Neon PostgreSQL** | Free tier | $0 |
| **Let's Encrypt TLS** | Free SSL certificates | $0 |
| **Custom Domain** | ~$10/year (optional) | ~$0.83/month |

**Total**: **$0 - $1/month** (depending on whether you purchase custom domain)

**Note**: Always Free tiers have limits. Monitor usage to avoid unexpected charges.

---

## 10. Production Readiness Checklist

Before deploying to production:

- [ ] All external services verified and working
- [ ] Database migrations tested on staging
- [ ] CI/CD pipeline tested on feature branch
- [ ] Monitoring and logging configured
- [ ] Backup strategy in place (Neon DB auto-backups)
- [ ] Rollback procedure documented
- [ ] Team trained on troubleshooting
- [ ] Hackathon demo video recorded

---

**Setup Guide Status**: ✅ Complete - All external services documented with step-by-step instructions.

**Total Setup Time**: 2-3 hours (one-time setup)

**Next Steps**:
1. Complete all verification checklists
2. Deploy to OKE cluster using Helm charts
3. Test end-to-end functionality
4. Configure CI/CD pipeline with GitHub Actions
5. Monitor production deployment
