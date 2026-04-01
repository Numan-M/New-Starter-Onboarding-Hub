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

resource "azurerm_container_registry" "acr" {
  name                = "nsoh-acr"
  resource_group_name = var.resource_group_name
  location            = var.location
  sku                 = "Basic"
}

# resource "azurerm_role_assignment" "acr_pull" {
#   scope                = azurerm_container_registry.acr.id
#   role_definition_name = "AcrPull"
#   principal_id         = azurerm_kubernetes_cluster.aks.kubelet_identity[0].object_id
# }

# resource "azurerm_role_assignment" "acr_push" {
#   scope                            = azurerm_container_registry.acr.id
#   role_definition_name             = "AcrPush"
#   principal_id                     = azurerm_kubernetes_cluster.aks.kubelet_identity[0].object_id
#   skip_service_principal_aad_check = true
# }

# resource "azurerm_role_assignment" "acr_tasks_contributor" {
#   scope                = azurerm_container_registry.acr.id
#   role_definition_name = "Container Registry Tasks Contributor"
#   principal_id         = azurerm_kubernetes_cluster.aks.kubelet_identity[0].object_id
# }

# resource "azurerm_role_assignment" "reader" {
#   scope                = azurerm_container_registry.acr.id
#   role_definition_name = "Reader"
#   principal_id         = azurerm_kubernetes_cluster.aks.kubelet_identity[0].object_id
# }

output "client_certificate" {
  value     = azurerm_kubernetes_cluster.aks.kube_config[0].client_certificate
  sensitive = true
}

output "kube_config" {
  value = azurerm_kubernetes_cluster.aks.kube_config_raw

  sensitive = true
}

