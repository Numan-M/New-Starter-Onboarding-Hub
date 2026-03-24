pipeline {
    agent {
        kubernetes {
            yaml '''
                apiVersion: v1
                kind: Pod
                metadata:
                    labels:
                        jenkins: agent
                spec:
                    serviceAccountName: default
                    containers:
                    - name: azure-cli
                    image: mcr.microsoft.com/azure-cli:latest
                    command:
                    - cat
                    tty: true
                    - name: kubectl
                    image: bitnami/kubectl:latest
                    command:
                    - cat
                    tty: true
                '''
        }
    }
    environment {
        AZURE_SUBSCRIPTION_ID = credentials('azure-subscription-id')
        REGISTRY = "numanepa.azurecr.io"
        ACR_NAME = "NumanEPA"
        RG_NAME = "NumanEPA"
        IMAGE_NAME = "epa/nsoh"
        AKS_CLUSTER_NAME = "Jenkins-NM"
        IMAGE_TAG = "${BUILD_NUMBER}"
    }

    stages {
            stage('Checkout') {
                steps {
                    checkout scm
                }
            }
    

        stage('Log in to Azure') {
            steps {
                container('azure-cli') {
                        sh 'az login --identity'
                        sh 'az account set --subscription $AZURE_SUBSCRIPTION_ID'
                        sh 'az account show'
                }
            }
        }

        stage('Build and Push Docker Image') {
            steps {
                container('azure-cli') {
                    sh "az acr build --registry ${ACR_NAME} --resource-group ${RG_NAME} --image ${IMAGE_NAME}:${IMAGE_TAG} --file Dockerfile ." 
                }
            }
        }

        stage('Deploy to AKS') {
            steps {
                container('azure-cli') {
                    sh "az aks get-credentials --resource-group ${RG_NAME} --name ${AKS_CLUSTER_NAME}"
                    sh "kubectl set image deployment/nsoh-dev nsoh=${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} -n nsoh-dev"
                }
            }
        }
        
    }
}