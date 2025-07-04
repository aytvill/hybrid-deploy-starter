# Hybrid Deploy Starter

This is a secure, flexible starter for deploying to both DigitalOcean (via OpenTofu) and VPS/bare-metal (via Ansible + Podman).

## Components
- **OpenTofu**: for provisioning DigitalOcean droplets
- **Ansible**: for configuring the OS and deploying apps
- **Podman**: for rootless containers with systemd
- **SOPS**: for secrets management
- **CI/CD**: via SSH + Ansible or GitOps

## Usage
1. Configure your DigitalOcean token and SSH key fingerprint in opentofu/terraform.tfvars
2. Run:
   ```
   cd opentofu
   tofu init && tofu apply
   ```
3. Deploy app:
   ```
   ./deploy/ci-cd.sh
   ```
