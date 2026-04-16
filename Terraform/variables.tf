variable "location" {
  type    = string
  default = "uksouth"
}

variable "resource_group_name" {
  type    = string
  default = "nsoh-rg"
}

variable "Subscription_id" {
  type        = string
  description = "The Azure subscription ID"
  sensitive   = true
}


