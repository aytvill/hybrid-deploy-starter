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
