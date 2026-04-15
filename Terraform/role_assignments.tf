# resource "azurerm_role_assignment" "aks_cluster_user" {
#   scope                = azurerm_kubernetes_cluster.aks.id
#   role_definition_name = "Azure Kubernetes Service Cluster User Role"
#   principal_id         = azurerm_kubernetes_cluster.aks.identity[0].principal_id
# }

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
