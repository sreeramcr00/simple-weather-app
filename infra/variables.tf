variable "resource_group_name" {
  type    = string
  default = "weatherapi-rg"
}
variable "location" {
  type = string
  default =  "East Asia"
}
variable "project_name" {
  type    = string
  default = "weatherapi"
}

variable "app_service_name" {
  type    = string
  default = "weatherapi-app"
}

variable "db_admin" {
  type    = string
  default = "adminuser"
}

variable "db_name" {
  type    = string
  default = "weatherdb"
}

variable "db_password" {
  type      = string
  sensitive = true
}

variable "secret_key" {
  type      = string
  sensitive = true
}

variable "openweather_api_key" {
  type      = string
  sensitive = true
}
