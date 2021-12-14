resource "google_project" "valheim" {
  name            = "valheim"
  project_id      = "valheim-rdkr-uk"
  billing_account = local.billing_account
  org_id          = data.google_organization.rdkr_uk.org_id
}
