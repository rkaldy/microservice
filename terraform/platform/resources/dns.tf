resource "google_dns_managed_zone" "managed_zone" {
  name        = "managed-zone"
  dns_name    = "${var.domain}."
}

output "nameservers" {
  value = google_dns_managed_zone.managed_zone.name_servers
}

resource "google_compute_global_address" "external_ip" {
  name = "external-ip"
}

resource "google_dns_record_set" "dns" {
  name         = "*.${var.domain}."
  type         = "A"
  ttl          = 300
  managed_zone = google_dns_managed_zone.managed_zone.name

  rrdatas = [
    google_compute_global_address.external_ip.address
  ]
}
