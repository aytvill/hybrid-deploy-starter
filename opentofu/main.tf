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
