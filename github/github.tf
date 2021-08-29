resource "github_repository" "infra" {
  name        = "infra"
  description = "☁️ personal infra (digital ocean k8s, DNS, etc)"
}

resource "github_actions_secret" "foundry_terraform_token" {
  repository      = github_repository.infra.name
  secret_name     = "terraform_token"
  plaintext_value = var.terraform_token
}

resource "github_actions_secret" "foundry_do_token" {
  repository      = github_repository.infra.name
  secret_name     = "do_token"
  plaintext_value = var.do_token
}

resource "github_actions_secret" "foundry_cloudflare_token" {
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
