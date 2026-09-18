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
                    call venv\\Scripts\\activate.bat
                    venv\\Scripts\\python.exe -m pip install --upgrade pip
                    venv\\Scripts\\python.exe -m pip install -r requirements.txt
                '''
            }
        }

        stage('Установка зависимостей') {
            steps {
                bat '''
                    venv\\Scripts\\python.exe -m pip list
                '''
            }
        }

        stage('Django запуск') {
            steps {
                bat '''
                    venv\\Scripts\\python.exe manage.py check
                '''
            }
        }

        stage('Запуск тестов') {
            steps {
                bat '''
                    venv\\Scripts\\python.exe -m pytest --disable-warnings -q
                '''
            }
        }
    }

    post {
        success {
            echo 'CI ок.'
        }
        failure {
            echo 'CI упал.'
        }
    }
}