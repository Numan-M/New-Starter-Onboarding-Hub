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

        stage('Build with Kaniko') {
            steps {
                sh """
                docker run --rm \
                  -v \$(pwd):/workspace \
                  -v /kaniko/.docker:/kaniko/.docker \
                  gcr.io/kaniko-project/executor:latest \
                  --dockerfile /workspace/Dockerfile \
                  --context /workspace \
                  --destination $REGISTRY/$IMAGE_NAME:$IMAGE_TAG
                """
            }
        }

    }
}