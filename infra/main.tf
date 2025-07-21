terraform {
  backend "azurerm" {
    resource_group_name  = "practice-rg"
    storage_account_name = "sreestoragelearn"    # must be globally unique
    container_name       = "tfstate"
    key                  = "infra/terraform.tfstate"
  }
}


provider "azurerm" {
  use_msi              = false
  use_cli              = true
  features {}
}

resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location
}

resource "azurerm_service_plan" "plan" {
  name                = "${var.project_name}-plan"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  os_type             = "Linux"
  sku_name            = "B1"
}

resource "azurerm_linux_web_app" "app" {
  name                = var.app_service_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  service_plan_id     = azurerm_service_plan.plan.id

  site_config {
    application_stack {
      python_version = "3.11"
    }
    always_on = true
  }

  app_settings = {
    "WEBSITE_RUN_FROM_PACKAGE" = "1"
    "SCM_DO_BUILD_DURING_DEPLOYMENT" = "true"
    "DATABASE_URL"             = "postgresql+psycopg2://${var.db_admin}:${var.db_password}@${azurerm_postgresql_flexible_server.db.fqdn}:5432/${var.db_name}"
    "SECRET_KEY"               = var.secret_key
    "OPENWEATHER_API_KEY"      = var.openweather_api_key
  }
}

resource "azurerm_postgresql_flexible_server" "db" {
  name                   = "${var.project_name}-db"
  resource_group_name    = azurerm_resource_group.rg.name
  location               = azurerm_resource_group.rg.location
  administrator_login    = var.db_admin
  administrator_password = var.db_password
  sku_name               = "B_Standard_B1ms"
  storage_mb             = 32768
  version                = "14"
  zone                   = "1"

  authentication {
    active_directory_auth_enabled = false
    password_auth_enabled         = true
  }

  depends_on = [azurerm_resource_group.rg]
}
resource "azurerm_postgresql_flexible_server_firewall_rule" "allow_app" {
  name       = "allow-azure-app-service"
  server_id  = azurerm_postgresql_flexible_server.db.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"
}

resource "azurerm_postgresql_flexible_server_database" "weatherdb" {
  name      = var.db_name
  server_id = azurerm_postgresql_flexible_server.db.id
  collation = "en_US.utf8"
  charset   = "UTF8"
}
