from pathlib import Path
import shutil

# Define the folder structure for the project
project_structure = {
    "hybrid-deploy-starter": {
        "opentofu": ["main.tf", "variables.tf", "outputs.tf"],
        "ansible": {
            "inventory": ["hosts.yml"],
            "roles": {
                "app": {
                    "tasks": ["main.yml"],
                    "templates": []
                }
            },
            "": ["playbook.yml", "ansible.cfg"]
        },
        "deploy": {
            "secrets": ["app.env.yaml"],
            "": ["ci-cd.sh"]
        },
        "container": ["Containerfile", "podman-compose.yml"],
        "": [".sops.yaml", ".gitignore", "README.md"]
    }
}

# Helper function to create directories and files
def create_structure(base_path, structure):
    for name, content in structure.items():
        current_path = base_path / name
        current_path.mkdir(parents=True, exist_ok=True)
        if isinstance(content, list):
            for file in content:
                (current_path / file).touch()
        elif isinstance(content, dict):
            create_structure(current_path, content)

# Set up base directory
base_dir = Path("/mnt/data/hybrid-deploy-starter")
if base_dir.exists():
    shutil.rmtree(base_dir)
base_dir.mkdir(parents=True)

# Create the project structure
create_structure(base_dir.parent, project_structure)

# Define the content to be written to each file
files_to_write = {
    "opentofu/main.tf": """
provider "digitalocean" {
  token = var.do_token
}

resource "digitalocean_droplet" "web" {
  image  = "ubuntu-22-04-x64"
  name   = "web-1"
  region = "fra1"
  size   = "s-1vcpu-1gb"
  ssh_keys = [var.ssh_key_fingerprint]

  tags = ["web"]
}

output "droplet_ip" {
  value = digitalocean_droplet.web.ipv4_address
}
""",
    "opentofu/variables.tf": """
variable "do_token" {
  type      = string
  sensitive = true
}

variable "ssh_key_fingerprint" {
  type = string
}
""",
    "opentofu/outputs.tf": """
output "droplet_ip" {
  value = digitalocean_droplet.web.ipv4_address
}
""",
    "ansible/playbook.yml": """
- name: Configure and deploy app
  hosts: web
  become: true
  roles:
    - app
""",
    "ansible/ansible.cfg": """
[defaults]
inventory = inventory/hosts.yml
host_key_checking = False
""",
    "ansible/inventory/hosts.yml": """
all:
  hosts:
    web:
      ansible_host: {{ host_ip }}
      ansible_user: root
""",
    "ansible/roles/app/tasks/main.yml": """
- name: Install Podman
  ansible.builtin.apt:
    name: podman
    state: present
    update_cache: true

- name: Run container with systemd unit
  ansible.builtin.copy:
    dest: /etc/systemd/system/myapp.service
    content: |
      [Unit]
      Description=My App Container
      After=network.target

      [Service]
      ExecStart=/usr/bin/podman run --rm -p 80:80 my-image
      Restart=always

      [Install]
      WantedBy=multi-user.target

- name: Enable and start service
  ansible.builtin.systemd:
    name: myapp
    enabled: true
    state: started
""",
    "deploy/secrets/app.env.yaml": """
apiVersion: v1
kind: Secret
metadata:
  name: app-env
type: Opaque
stringData:
  APP_SECRET: ENC[AES256_GCM,data:xxxx...,tag:xxx...,type:str]
""",
    "deploy/ci-cd.sh": """
#!/bin/bash
# Simple deploy script using Ansible and dynamic inventory

set -e

HOST_IP=$(cd opentofu && tofu output -raw droplet_ip)
echo "Deploying to $HOST_IP"

# Replace host_ip in inventory
sed "s/{{ host_ip }}/$HOST_IP/" ansible/inventory/hosts.yml > ansible/inventory/hosts_temp.yml
mv ansible/inventory/hosts_temp.yml ansible/inventory/hosts.yml

# Run playbook
cd ansible
ansible-playbook playbook.yml
""",
    "container/Containerfile": """
FROM alpine:latest
RUN apk add --no-cache python3
CMD ["python3", "-m", "http.server", "80"]
""",
    "container/podman-compose.yml": """
version: "3"
services:
  app:
    build: .
    ports:
      - "8080:80"
""",
    ".sops.yaml": """
creation_rules:
  - encrypted_regex: '^(data|stringData)$'
    path_regex: '.*\\.yaml$'
    key_groups:
      - age:
          - AGE-SECRET-KEY-1XXXXXXXXXXXXXXX
""",
    "README.md": """
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
