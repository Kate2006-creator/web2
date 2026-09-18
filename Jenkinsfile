pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Подготовить среду Python') {
            steps {
                bat '''
                    "C:\\Users\\Tecno\\AppData\\Local\\Programs\\Python\\Python312\\python.exe" -m venv venv
                    venv\\Scripts\\python.exe -m pip install --upgrade pip
                    venv\\Scripts\\python.exe -m pip install -r requirements.txt
                '''
            }
        }

        stage('Установка зависимостей') {
            steps {
                bat 'venv\\Scripts\\python.exe -m pip list'
            }
        }

        stage('Запуск тестов') {
            steps {
                bat 'venv\\Scripts\\python.exe -m pytest --disable-warnings -q'
            }
        }

        stage('Django') {
            steps {
                bat '''
                    start /B venv\\Scripts\\python.exe manage.py runserver 8000 > django.log 2>&1
                    timeout /t 5 /nobreak
                    echo Django запущен на http://localhost:8000/
                '''
            }
        }

        stage('Vue') {
            steps {
                bat '''
                    cd /d "%WORKSPACE%\\client"
                    if not exist node_modules (
                        npm install
                    )
                    start /B npm run serve -- --port 3000 > vue.log 2>&1
                    timeout /t 10 /nobreak
                    echo Vue запущен на http://localhost:3000/
                '''
            }
        }
    }

    post {
        success {
            echo 'CI ок. Серверы запущены.'
        }
        failure {
            echo 'CI упал.'
        }
    }
}