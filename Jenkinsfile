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
    - name: azure-kubectl
      image: numanepa.azurecr.io/tools/azure-kubectl:latest
      command:
      - cat
      tty: true

    - name: python
      image: numanepa.azurecr.io/python:latest
      command:
      - cat
      tty: true

    - name: trufflehog
      image: numanepa.azurecr.io/tools/trufflehog:latest
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
        IMAGE_TAG = "dev.${BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Install Dependencies') {
            steps {
                container('python') {
                    sh '''
                    pip install -r requirements.txt
                    '''
                }
            }
        }
        stage('Security Scan: pip-audit') {
            steps {
                container('python') {
                    sh '''
                    echo "Generating JSON report:"
                    pip-audit -r requirements.txt -f json -o pip-audit-report.json

                    echo "Report:"
                    pip-audit -r requirements.txt

                    echo "Strict mode (fail on any vulnerability)"
                    pip-audit -r requirements.txt --strict
                    '''
                }
                
                archiveArtifacts artifacts: 'pip-audit-report.json', fingerprint: true

            }
        }
        stage('Security Scan: Bandit') {
            steps {
                container('python') {
                    sh '''
                    echo "Bandit scan:"

                    bandit -r . \
                    -f json \
                    -o bandit-report.json

                    echo "Readable output:"
                    bandit -r .

                    echo "Scan with high severity only:"
                    bandit -r . -lll
                    '''
                }

                archiveArtifacts artifacts: 'bandit-report.json', fingerprint: true
            }
        }
        
        stage('Security Scan: TruffleHog') {
            steps {
                container('trufflehog') {
                    sh '''
                    echo "TruffleHog scan:"

                    trufflehog filesystem /repo \
                    --only-verified \
                    --exclude-paths=/repo/.trufflehogignore \
                    --json > trufflehog-report.json
                    '''
                }

                archiveArtifacts artifacts: 'trufflehog-report.json', fingerprint: true
            }
        }
        stage('Run Tests') {
            steps {
                container('python') {
                    sh '''
                    export SECRET_KEY=dev-test-key
                    export DATABASE_URL=sqlite:///:memory:
                    pytest -v
                    '''
                }
            }
        }

        stage('Log in to Azure') {
            steps {
                container('azure-kubectl') {
                        sh 'az login --identity'
                        sh 'az account set --subscription $AZURE_SUBSCRIPTION_ID'
                }
            }
        }

        stage('Build and Push Docker Image') {
            steps {
                container('azure-kubectl') {
                    sh "az acr build --registry ${ACR_NAME} --resource-group ${RG_NAME} --image ${IMAGE_NAME}:${IMAGE_TAG} --file Dockerfile ." 
                }
            }
        }
        stage('Run DB Migrations') {
            steps {
                container('azure-kubectl') {
                    sh "az aks get-credentials --resource-group ${RG_NAME} --name ${AKS_CLUSTER_NAME}"

                    sh """
                    SECRET_KEY=\$(kubectl get secret app-secrets -n nsoh-dev -o jsonpath='{.data.SECRET_KEY}' | base64 --decode)

                    kubectl run db-migrate-${BUILD_NUMBER} \
                    --rm -i --restart=Never \
                    --image=${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} \
                    --namespace nsoh-dev \
                    --env DATABASE_URL=postgresql://appuser:apppass@postgres:5432/appdb \
                    --env SECRET_KEY=\$SECRET_KEY \
                    --command -- flask db upgrade
                    """
                }
            }
        }
        stage('Deploy to AKS') {
            steps {
                container('azure-kubectl') {
                    sh "az aks get-credentials --resource-group ${RG_NAME} --name ${AKS_CLUSTER_NAME}"
                    sh "kubectl set image deployment/flask-app flask-app=${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} -n nsoh-dev"  
                }            
            }
        }
        
    }
}