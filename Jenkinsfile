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
                    "C:\\Users\\Tecno\\AppData\\Local\\Programs\\Python\\Python312\\python.exe" -m venv venv
                    call venv\\Scripts\\activate.bat
                    venv\\Scripts\\python.exe -m pip install --upgrade pip
                    venv\\Scripts\\python.exe -m pip install -r requirements.txt
                '''
            }
        }

        stage('Install dependencies') {
            steps {
                bat '''
                    venv\\Scripts\\python.exe -m pip list
                '''
            }
        }

        stage('Django checks') {
            steps {
                bat '''
                    venv\\Scripts\\python.exe manage.py check
                '''
            }
        }

        stage('Run tests') {
            steps {
                bat '''
                    venv\\Scripts\\python.exe -m pytest --maxfail=1 --disable-warnings -q --junitxml=report.xml
                '''
            }
        }
    }

    post {
        always {
            script {
                if (fileExists('report.xml')) {
                    junit 'report.xml'
                } else {
                    echo '⚠️ report.xml не найден — pytest не создал отчёт.'
                }
            }
        }
        success {
            echo ' CI ок.'
        }
        failure {
            echo ' CI упал.'
        }
    }
}