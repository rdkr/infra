resource "google_project" "minecraft" {
  name            = "minecraft"
  project_id      = "minecraft-rdkr-uk"
  billing_account = local.billing_account
  org_id          = data.google_organization.rdkr_uk.org_id
}

resource "google_project_service" "minecraft_compute" {
  project = google_project.minecraft.project_id
  service = "compute.googleapis.com"
}

# resource "google_project_iam_binding" "minecraft_editor" {
#   project = google_project.minecraft.project_id
#   role    = "roles/editor"

#   members = [

#   ]
# }
