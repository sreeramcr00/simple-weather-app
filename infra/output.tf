output "app_service_name" {
  value = azurerm_linux_web_app.app.name
}

output "resource_group_name" {
  value = azurerm_resource_group.rg.name
}

output "app_url" {
  value = azurerm_linux_web_app.app.default_hostname
}

output "database_url" {
  value = "postgresql+psycopg2://${var.db_admin}:${var.db_password}@${azurerm_postgresql_flexible_server.db.fqdn}:5432/${var.db_name}"
  sensitive = true
}
