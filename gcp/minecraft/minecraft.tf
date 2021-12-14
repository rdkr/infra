resource "google_service_account" "minecraft" {
  account_id   = "minecraft"
  display_name = "minecraft"
}

resource "google_compute_firewall" "minecraft" {
  name    = "minecraft"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["25565"]
  }

  allow {
    protocol = "udp"
    ports    = ["25565", "19132", "19133"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["minecraft"]
}

resource "google_compute_instance" "minecraft" {
  # desired_status = "RUNNING"
  desired_status = "TERMINATED"

  name         = "minecraft"
  machine_type = "e2-small"
  zone         = "europe-west4-a"

  tags = [google_compute_firewall.minecraft.name]

  boot_disk {
    initialize_params {
      image = "cos-cloud/cos-93-16623-39-30"
    }
  }

  network_interface {
    network = "default"
    access_config {} // create ephemeral ip
  }

  metadata = {
    user-data = templatefile("${path.module}/user_data.yaml", {})
  }

  service_account {
    email  = google_service_account.minecraft.email
    scopes = ["cloud-platform"]
  }
}
