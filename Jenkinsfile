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
        AZURE_SUBSCRIPTION_ID = credentials('AZURE_SUBSCRIPTION_ID')
        REGISTRY = "numanepa.azurecr.io"
        ACR_NAME = "NumanEPA"
        IMAGE_NAME = "epa/nsoh"
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
                    sh """
                        az login --identity"""
                       // az account set --subscription ${AZURE_SUBSCRIPTION_ID}
                      //  az account show
                    
                
            }
        }
        
    }
}
}

