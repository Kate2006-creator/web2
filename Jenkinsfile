pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Prepare Python env') {
            steps {
                bat '''
                    python -m venv venv
                    call venv\\Scripts\\activate.bat
                    python -m pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Install dependencies') {
            steps {
                bat '''
                    call venv\\Scripts\\activate.bat
                    pip list
                '''
            }
        }

        stage('Django checks') {
            steps {
                bat '''
                    call venv\\Scripts\\activate.bat
                    python manage.py check
                '''
            }
        }

        stage('Run tests') {
            steps {
                bat '''
                    call venv\\Scripts\\activate.bat
                    pytest --maxfail=1 --disable-warnings -q --junitxml=report.xml
                '''
            }
        }
    }

    post {
        always {
            junit 'report.xml'
        }
        success {
            echo ' CI ок.'
        }
        failure {
            echo 'CI упал.'
        }
    }
}