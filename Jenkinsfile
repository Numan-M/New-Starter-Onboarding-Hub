pipeline {
    agent any
    environment {
        REGISTRY = "numanepa.azurecr.io"
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
                docker build -t $REGISTRY/$IMAGE_NAME:$IMAGE_TAG .
                """
            }
        }
        
    }
}

