resource "google_certificate_manager_dns_authorization" "dns_auth" {
  project = var.project_id
  name    = "dns-auth"
  domain  = var.domain
}

resource "google_dns_record_set" "dns_auth_wildcard_record" {
  project      = var.project_id
  name         = google_certificate_manager_dns_authorization.dns_auth.dns_resource_record[0].name
  type         = google_certificate_manager_dns_authorization.dns_auth.dns_resource_record[0].type
  managed_zone = google_dns_managed_zone.managed_zone.name
  ttl          = 300
  rrdatas      = [
    google_certificate_manager_dns_authorization.dns_auth.dns_resource_record[0].data
  ]
}

resource "google_certificate_manager_certificate" "global" {
  project = var.project_id
  name    = "global"
  scope   = "DEFAULT"
  managed {
    domains            = [var.domain, "*.${var.domain}"]
    dns_authorizations = [google_certificate_manager_dns_authorization.dns_auth.id]
  }
}

resource "google_certificate_manager_certificate_map" "certificate_map" {
  project = var.project_id
  name    = "certificate-map"
}

resource "google_certificate_manager_certificate_map_entry" "certificate_map_entry" {
  project      = var.project_id
  name         = "default"
  map          = google_certificate_manager_certificate_map.certificate_map.name
  matcher      = "PRIMARY"
  certificates = [google_certificate_manager_certificate.global.id]
}
