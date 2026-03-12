resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location
}

resource "azurerm_kubernetes_cluster" "aks" {
  name                = "nsoh-aks-cluster"
  location            = var.location
  resource_group_name = var.resource_group_name
  dns_prefix          = "nsoh-dev"

  default_node_pool {
    name       = "default"
    node_count = 1
    vm_size    = "Standard_D4as_v5"
  }

  identity {
    type = "SystemAssigned"
  }

  tags = {
    Environment = "sandpit"
  }
}

output "client_certificate" {
  value     = azurerm_kubernetes_cluster.aks.kube_config[0].client_certificate
  sensitive = true
}

output "kube_config" {
  value = azurerm_kubernetes_cluster.aks.kube_config_raw

  sensitive = true
}

