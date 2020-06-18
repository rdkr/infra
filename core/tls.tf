provider "acme" {
  server_url = "https://acme-staging-v02.api.letsencrypt.org/directory"
}

resource "tls_private_key" "hermes_gateway" {
  algorithm = "RSA"
}

resource "acme_registration" "hermes_gateway" {
  account_key_pem = "${tls_private_key.hermes_gateway.private_key_pem}"
  email_address   = "neel@rdkr.uk"
}

resource "acme_certificate" "hermes_gateway" {
  account_key_pem           = "${acme_registration.hermes_gateway.account_key_pem}"
  common_name               = "hermes-gateway.rdkr.uk"

  dns_challenge {
    provider = "cloudflare"
  }
}
