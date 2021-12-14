resource "google_project" "minecraft" {
  name            = "minecraft"
  project_id      = "minecraft-rdkr-uk"
  billing_account = local.billing_account
  org_id          = data.google_organization.rdkr_uk.org_id
}

resource "google_project_service" "minecraft_services" {
  for_each = toset([
    "compute.googleapis.com",
    "iam.googleapis.com",
  ])
  project = google_project.minecraft.project_id
  service = each.key
}

resource "google_service_account" "minecraft_github_actions" {
  project = google_project.minecraft.project_id
  account_id   = "minecraft-github-actions"
}
resource "google_project_iam_member" "minecraft_github_actions" {
  project = google_project.minecraft.project_id
  role    = "roles/editor"
  member  = "serviceAccount:${google_service_account.minecraft_github_actions.email}"
}

resource "google_service_account_key" "minecraft_github_actions" {
  service_account_id = google_service_account.minecraft_github_actions.name
  public_key_type    = "TYPE_X509_PEM_FILE"
}

output "minecraft_github_actions_key" {
  value = chomp(base64decode(google_service_account_key.minecraft_github_actions.private_key))
  sensitive = true
}

# resource "google_project_iam_binding" "minecraft_editor" {
#   project = google_project.minecraft.project_id
#   role    = "roles/editor"

#   members = [

#   ]
# }
