pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps { checkout scm }
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

        stage('Миграции БД') {
            when {
                anyOf {
                    branch 'dev'
                    branch 'master'
                }
            }
            steps {
                bat 'venv\\Scripts\\python.exe manage.py migrate'
            }
        }

        stage('Запуск тестов') {
            steps {
                bat 'venv\\Scripts\\python.exe -m pytest --disable-warnings -q'
            }
        }

        stage('Перезапуск Django') {
            when {
                anyOf {
                    branch 'dev'
                    branch 'master'
                }
            }
            steps {
                bat '''
                    "D:\\Tools\\nssm\\nssm-2.24\\win64\\nssm.exe" stop DjangoServer
                    ping 127.0.0.1 -n 3 > nul
                    "D:\\Tools\\nssm\\nssm-2.24\\win64\\nssm.exe" start DjangoServer
                    ping 127.0.0.1 -n 4 > nul
                    echo Django  http://localhost:8000/
                '''
            }
        }

        stage('Перезапуск Vue') {
            when {
                anyOf {
                    branch 'dev'
                    branch 'master'
                }
            }
            steps {
                bat '''
                    "D:\\Tools\\nssm\\nssm-2.24\\win64\\nssm.exe" stop VueServer
                    ping 127.0.0.1 -n 3 > nul
                    "D:\\Tools\\nssm\\nssm-2.24\\win64\\nssm.exe" start VueServer
                    ping 127.0.0.1 -n 4 > nul
                    echo Vue http://localhost:3000/
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