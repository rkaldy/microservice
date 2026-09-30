resource "google_dns_managed_zone" "managed_zone" {
  name     = "managed-zone"
  dns_name = "${var.domain}."
}

resource "google_compute_global_address" "external_ip" {
  name = "external-ip"
}

resource "google_dns_record_set" "dns_root" {
  name         = "${var.domain}."
  type         = "A"
  ttl          = 300
  managed_zone = google_dns_managed_zone.managed_zone.name

  rrdatas = [google_compute_global_address.external_ip.address]
}

resource "google_dns_record_set" "dns_subdomain" {
  name         = "*.${var.domain}."
  type         = "A"
  ttl          = 300
  managed_zone = google_dns_managed_zone.managed_zone.name

  rrdatas = [google_compute_global_address.external_ip.address]
}
