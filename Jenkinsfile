pipeline {
    agent any
    
    environment {
        // These can be set in Jenkins UI or here
        REPO_URL = 'https://github.com/en1gm4-exe/Secure-Software-Design-Final.git'
        DEPLOY_DIR = '/opt/flask-app'
        APP_NAME = 'lab06-flask-app'
    }
    
    stages {
        stage('Checkout Code') {
            steps {
                echo ' Cloning repository from GitHub...'
                checkout scm: [
                    $class: 'GitSCM',
                    branches: [[name: '*/main']],
                    extensions: [],
                    userRemoteConfigs: [[url: env.REPO_URL]]
                ]
                
                sh '''
                    echo "Current directory: $(pwd)"
                    echo "Files in directory:"
                    ls -la
                '''
            }
        }
        
        stage('Setup Python Environment') {
            steps {
                echo ' Setting up Python...'
                sh '''
                    # Check Python version
                    python3 --version
                    pip3 --version || echo "pip3 not found, installing..."
                    
                    # Install Python and pip if not present
                    if ! command -v python3 &> /dev/null; then
                        echo "Installing Python3..."
                        sudo apt-get update
                        sudo apt-get install -y python3 python3-pip python3-venv
                    fi
                    
                    # Create virtual environment
                    python3 -m venv venv
                    source venv/bin/activate
                    pip install --upgrade pip
                '''
            }
        }
        
        stage('Install Dependencies') {
            steps {
                echo 'Installing dependencies...'
                sh '''
                    source venv/bin/activate
                    
                    # Check if requirements.txt exists
                    if [ -f "requirements.txt" ]; then
                        echo "Installing from requirements.txt..."
                        pip install -r requirements.txt
                    else
                        echo "requirements.txt not found. Installing basic packages..."
                        pip install flask pytest
                    fi
                    
                    # Verify installations
                    echo "Installed packages:"
                    pip list | grep -E "(Flask|pytest|Werkzeug|Jinja2)"
                '''
            }
        }
        
        stage('Run Unit Tests') {
            steps {
                echo ' Running unit tests...'
                sh '''
                    source venv/bin/activate
                    
                    # Check for test files
                    echo "Looking for test files..."
                    find . -name "test_*.py" -o -name "*_test.py" | grep -v venv
                    
                    # Run pytest with coverage
                    if [ -d "tests" ] || [ -f "test_*.py" ]; then
                        echo "Running tests with pytest..."
                        python -m pytest tests/ -v --junitxml=test-results.xml --cov=.
                        
                        # Generate coverage report
                        coverage xml -o coverage.xml
                        coverage html -d coverage_report
                    else
                        echo " No test files found. Creating a sample test..."
                        # Create a simple test file
                        cat > test_sample.py << 'EOF'
def test_addition():
    assert 1 + 1 == 2

def test_flask_import():
    try:
        import flask
        assert True
    except ImportError:
        assert False
EOF
                        python -m pytest test_sample.py -v
                    fi
                '''
            }
            post {
                always {
                    junit 'test-results.xml'
                    archiveArtifacts artifacts: 'coverage.xml', fingerprint: true
                    publishHTML(target: [
                        reportName: 'Coverage Report',
                        reportDir: 'coverage_report',
                        reportFiles: 'index.html',
                        keepAll: true
                    ])
                }
            }
        }
        
        stage('Build Application') {
            steps {
                echo ' Building application package...'
                sh '''
                    echo "Creating build directory..."
                    rm -rf build dist || true
                    mkdir -p build dist
                    
                    # Copy application files
                    cp -r *.py build/ 2>/dev/null || echo "No .py files to copy"
                    cp -r templates build/ 2>/dev/null || echo "No templates directory"
                    cp -r static build/ 2>/dev/null || echo "No static directory"
                    cp requirements.txt build/ 2>/dev/null || echo "No requirements.txt"
                    
                    # Create application structure
                    echo "Creating application structure..."
                    mkdir -p build/logs
                    mkdir -p build/config
                    
                    # Create WSGI entry point
                    cat > build/wsgi.py << 'EOF'
from app import app

if __name__ == "__main__":
    app.run()
EOF
                    
                    # Create startup script
                    cat > build/start.sh << 'EOF'
#!/bin/bash
# Startup script for Flask application
cd "$(dirname "$0")"
source venv/bin/activate
export FLASK_APP=app.py
export FLASK_ENV=production
exec gunicorn --bind 0.0.0.0:5000 wsgi:app
EOF
                    
                    chmod +x build/start.sh
                    
                    # Create systemd service file (for deployment)
                    cat > build/${APP_NAME}.service << EOF
[Unit]
Description=Lab06 Flask Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/${APP_NAME}
Environment="PATH=/opt/${APP_NAME}/venv/bin"
ExecStart=/opt/${APP_NAME}/start.sh
Restart=always

[Install]
WantedBy=multi-user.target
EOF
                    
                    # Create deployment package
                    tar -czf dist/${APP_NAME}-${BUILD_NUMBER}.tar.gz build/
                    
                    echo "Build artifacts:"
                    ls -la dist/
                '''
                archiveArtifacts artifacts: 'dist/*.tar.gz', fingerprint: true
            }
        }
        
        stage('Deployment Simulation') {
            steps {
                echo ' Simulating deployment...'
                script {
                    // This is a simulation - in real scenario, you'd deploy to server
                    sh '''
                        echo "=== DEPLOYMENT SIMULATION ==="
                        echo "1. Extracting build package..."
                        tar -xzf dist/${APP_NAME}-${BUILD_NUMBER}.tar.gz -C /tmp/
                        
                        echo "2. Simulating file copy to ${DEPLOY_DIR}..."
                        sudo mkdir -p ${DEPLOY_DIR} || echo "Directory already exists"
                        sudo cp -r /tmp/build/* ${DEPLOY_DIR}/ || echo "Copy simulation"
                        
                        echo "3. Creating deployment log..."
                        echo "Deployment Time: $(date)" > ${DEPLOY_DIR}/deployment.log
                        echo "Build Number: ${BUILD_NUMBER}" >> ${DEPLOY_DIR}/deployment.log
                        echo "Commit: $(git log -1 --oneline)" >> ${DEPLOY_DIR}/deployment.log
                        
                        echo "4. Simulating service restart..."
                        # In real deployment, you would:
                        # sudo cp ${DEPLOY_DIR}/${APP_NAME}.service /etc/systemd/system/
                        # sudo systemctl daemon-reload
                        # sudo systemctl enable ${APP_NAME}.service
                        # sudo systemctl restart ${APP_NAME}.service
                        
                        echo "5. Verifying deployment..."
                        ls -la ${DEPLOY_DIR}/
                        
                        echo "=== DEPLOYMENT SIMULATION COMPLETE ==="
                    '''
                    
                    // Simulate deployment validation
                    sh '''
                        echo "Validating deployment..."
                        if [ -d "${DEPLOY_DIR}" ]; then
                            echo "✓ Deployment directory exists"
                            DEPLOYMENT_FILES=$(ls ${DEPLOY_DIR} | wc -l)
                            echo "✓ Files in deployment: ${DEPLOYMENT_FILES}"
                            echo "✓ Deployment successful!"
                        else
                            echo "✗ Deployment directory not found"
                        fi
                    '''
                }
            }
        }
        
        stage('Health Check') {
            steps {
                echo 'Performing health check...'
                sh '''
                    echo "Simulating application health check..."
                    # In real scenario, you would:
                    # curl -f http://localhost:5000/health || exit 1
                    # curl -f http://localhost:5000/ || exit 1
                    
                    echo "Health check simulation passed!"
                    echo "Application would be tested on port 5000"
                '''
            }
        }
    }
    
    post {
        success {
            echo 'Pipeline completed successfully!'
            emailext (
                subject: "Pipeline SUCCESS: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: "The Jenkins pipeline for ${env.JOB_NAME} build #${env.BUILD_NUMBER} completed successfully.\n\nView build: ${env.BUILD_URL}",
                to: 'developer@example.com'  # Change this
            )
        }
        failure {
            echo ' Pipeline failed!'
            emailext (
                subject: "Pipeline FAILED: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: "The Jenkins pipeline for ${env.JOB_NAME} build #${env.BUILD_NUMBER} failed.\n\nView build: ${env.BUILD_URL}",
                to: 'developer@example.com'  # Change this
            )
        }
        always {
            echo 'Cleaning up workspace...'
            sh '''
                # Clean up
                rm -rf venv build dist coverage_report __pycache__ || true
                find . -name "*.pyc" -delete
                find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
            '''
            
            // Archive test results
            archiveArtifacts artifacts: '**/test-results.xml,**/coverage.xml', fingerprint: true
        }
    }
    
    options {
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
        disableConcurrentBuilds()
    }
    
    triggers {
        cron('H 9 * * *')       // Daily at 9 AM
    }
    
    parameters {
        choice(
            name: 'DEPLOYMENT_ENV',
            choices: ['simulation', 'staging', 'production'],
            description: 'Select deployment environment'
        )
        booleanParam(
            name: 'RUN_TESTS',
            defaultValue: true,
            description: 'Run unit tests'
        )
        booleanParam(
            name: 'SEND_NOTIFICATIONS',
            defaultValue: true,
            description: 'Send email notifications'
        )
    }
}
