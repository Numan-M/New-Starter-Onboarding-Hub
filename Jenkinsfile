pipeline {
    agent any
    environment {
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
        stage('Build') {
            steps {
                sh """
                az --version
                az acr build --registry ${ACR_NAME} --image ${IMAGE_NAME}:${IMAGE_TAG} .
                """
            }
        }
        
    }
}

