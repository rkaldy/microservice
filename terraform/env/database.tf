resource "google_sql_database_instance" "db" {
  name                = "${var.env}-master"
  database_version    = var.database.type_version
  deletion_protection = var.database.deletion_protection

  settings {
    edition                     = var.database.edition
    tier                        = "db-custom-${var.database.cpu}-${var.database.memory * 1024}"
    disk_size                   = var.database.disk_size
    disk_autoresize             = var.database.disk_autoresize
    availability_type           = var.database.availability_type
    deletion_protection_enabled = var.database.deletion_protection

    dynamic "database_flags" {
      for_each = var.database.flags
      iterator = flag
      content {
        name  = flag.key
        value = flag.value
      }
    }

    backup_configuration {
      enabled    = var.database.backup_enabled
      start_time = var.database.backup_time
    }

    maintenance_window {
      day  = var.database.maintenance_day
      hour = var.database.maintenance_hour
    }

    insights_config {
      query_insights_enabled  = true
      query_string_length     = 1024
      record_application_tags = false
      record_client_address   = false
    }

    ip_configuration {
      ipv4_enabled = false
      private_network = data.google_compute_network.default.self_link
    }
  }
}

resource "google_sql_database" "db" {
  instance = google_sql_database_instance.db.name
  name     = "db"
}

resource "random_password" "db_user_password" {
  length  = 16
  special = false
}

resource "google_sql_user" "user" {
  instance = google_sql_database_instance.db.name
  name     = "user"
  password = random_password.db_user_password.result
}

resource "google_secret_manager_secret" "db_user_password" {
  secret_id = "${var.env}-db-password"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "db_user_password" {
  secret      = google_secret_manager_secret.db_user_password.id
  secret_data = random_password.db_user_password.result
}

resource "kubernetes_config_map" "db" {
  metadata {
    name      = "database"
    namespace = kubernetes_namespace.ns.metadata[0].name
  }

  data = {
    DB_TYPE  = lower(split("_", var.database.type_version)[0])
    DB_HOST  = google_sql_database_instance.db.ip_address[0].ip_address
    DB_NAME  = google_sql_database.db.name
    DB_USER  = google_sql_user.user.name
  }
}
