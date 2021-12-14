resource "github_repository" "infra" {
  name        = "infra"
  description = "☁️ personal infra (digital ocean k8s, DNS, etc)"
}

resource "github_actions_secret" "terraform_token" {
  repository      = github_repository.infra.name
  secret_name     = "terraform_token"
  plaintext_value = var.terraform_token
}

resource "github_actions_secret" "do_token" {
  repository      = github_repository.infra.name
  secret_name     = "do_token"
  plaintext_value = var.do_token
}

resource "github_actions_secret" "cloudflare_token" {
  repository      = github_repository.infra.name
  secret_name     = "cloudflare_token"
  plaintext_value = var.cloudflare_token
}

resource "github_actions_secret" "foundry_foundry_password" {
  repository      = github_repository.infra.name
  secret_name     = "foundry_password"
  plaintext_value = var.foundry_password
}

resource "github_actions_secret" "foundry_foundry_admin_key" {
  repository      = github_repository.infra.name
  secret_name     = "foundry_admin_key"
  plaintext_value = var.foundry_admin_key
}

data "terraform_remote_state" "infra_gcp_projects" {
  backend = "remote"

  config = {
    organization = "rdkr"
    workspaces = {
      name = "infra-gcp-projects"
    }
  }
}

resource "github_actions_secret" "minecraft_github_actions_key" {
  repository      = github_repository.infra.name
  secret_name     = "minecraft_github_actions_key"
  plaintext_value = data.terraform_remote_state.infra_gcp_projects.outputs.minecraft_github_actions_key
}
