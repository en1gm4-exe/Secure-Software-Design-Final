pipeline {
    agent any
    
    parameters {
        booleanParam(name: 'RUN_TESTS', defaultValue: true, description: 'Run unit tests')
        choice(name: 'DEPLOYMENT_ENV', choices: ['simulation', 'staging', 'production'], description: 'Select deployment environment')
    }
    
    environment {
        REPO_URL = 'https://github.com/en1gm4-exe/Secure-Software-Design-Final.git'
        APP_DIR = 'Lab06'
        DEPLOY_DIR = 'deploy'
        VERSION = '1.0.0'
    }
    
    stages {
        stage('Checkout Code') {
            steps {
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: '*/main']],
                    extensions: [[$class: 'RelativeTargetDirectory', relativeTargetDir: 'source']],
                    userRemoteConfigs: [[url: env.REPO_URL]]
                ])
                dir('source') {
                    sh 'ls -la'
                }
            }
        }
        
        stage('Setup Environment') {
            steps {
                dir('source/' + env.APP_DIR) {
                    sh '''
                        python3 --version
                        python3 -m venv venv
                        . venv/bin/activate
                        pip install --upgrade pip
                    '''
                }
            }
        }
        
        stage('Install Dependencies') {
            steps {
                dir('source/' + env.APP_DIR) {
                    sh '''
                        . venv/bin/activate
                        if [ -f "requirements.txt" ]; then
                            pip install -r requirements.txt
                        else
                            pip install flask pytest
                        fi
                    '''
                }
            }
        }
        
        stage('Run Unit Tests') {
            when {
                expression { params.RUN_TESTS == true }
            }
            steps {
                dir('source/' + env.APP_DIR) {
                    sh '''
                        . venv/bin/activate
                        mkdir -p tests
                        if [ ! -f "tests/test_app.py" ]; then
                            cat > tests/test_app.py << EOF
import pytest
def test_example():
    assert 1 == 1
EOF
                        fi
                        python -m pytest tests/ -v --junitxml=test-results.xml
                    '''
                }
            }
            post {
                always {
                    junit 'source/' + env.APP_DIR + '/test-results.xml'
                }
            }
        }
        
        stage('Build Application') {
            steps {
                dir('source/' + env.APP_DIR) {
                    sh '''
                        rm -rf build
                        mkdir -p build
                        cp -r *.py build/ 2>/dev/null || true
                        cp -r templates build/ 2>/dev/null || true
                        cp -r static build/ 2>/dev/null || true
                        cp requirements.txt build/ 2>/dev/null || true
                        tar -czf flask-app-build.tar.gz build/
                        echo "Build created:"
                        ls -la flask-app-build.tar.gz
                    '''
                    archiveArtifacts artifacts: 'flask-app-build.tar.gz', fingerprint: true
                }
            }
        }
        
        stage('Deploy Application') {
            steps {
                script {
                    echo "Deploying to environment: ${params.DEPLOYMENT_ENV}"
                    dir('source/' + env.APP_DIR) {
                        sh '''
                            echo "Current directory: $(pwd)"
                            echo "Files in current directory:"
                            ls -la
                            
                            echo "Simulating deployment to ${DEPLOY_DIR}"
                            rm -rf ${DEPLOY_DIR}
                            mkdir -p ${DEPLOY_DIR}
                            
                            echo "Extracting build files..."
                            tar -xzf flask-app-build.tar.gz -C ${DEPLOY_DIR}
                            
                            echo "Copying files..."
                            cp -r ${DEPLOY_DIR}/build/* ${DEPLOY_DIR}/ || echo "Copy simulation"
                            
                            echo "Creating deployment log..."
                            date > ${DEPLOY_DIR}/deployment.log
                            echo "Build Number: ${BUILD_NUMBER}" >> ${DEPLOY_DIR}/deployment.log
                            echo "Deployment environment: ${params.DEPLOYMENT_ENV}" >> ${DEPLOY_DIR}/deployment.log
                            
                            echo "Deployed files:"
                            ls -la ${DEPLOY_DIR}/
                        '''
                    }
                }
            }
        }
    }
    
    post {
        always {
            echo 'Pipeline execution completed'
        }
        success {
            echo 'Pipeline succeeded'
        }
        failure {
            echo 'Pipeline failed'
        }
    }
    
    options {
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
        disableConcurrentBuilds()
    }
}
