terraform{
  cloud {
    organization = "rdkr"

    workspaces {
      name = "infra-gcp-minecraft"
    }
  }
}

provider "google" {
  project = "minecraft-rdkr-uk"
  zone    = "europe-west4-a"
}

data "google_organization" "rdkr_uk" {
  domain = "rdkr.uk"
}
