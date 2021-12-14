terraform{
  cloud {
    organization = "rdkr"

    workspaces {
      name = "infra-gcp-minecraft"
    }
  }
    required_providers {
    cloudflare = {
      source = "cloudflare/cloudflare"
    }
    }
}

provider "google" {
  project = "minecraft-rdkr-uk"
  zone    = "europe-west4-a"
}

provider "cloudflare" {
  api_token = var.cloudflare_token
}
