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

        stage('Запуск тестов') {
            steps {
                bat 'venv\\Scripts\\python.exe -m pytest --disable-warnings -q'
            }
        }

        stage('Сборка Docker-образов') {
            when {
                anyOf {
                    branch 'dev'
                    branch 'master'
                }
            }
            steps {
                bat 'docker compose build'
            }
        }

       stage('Остановка локальных контейнеров') {
            when {
                anyOf {
                    branch 'dev'
                    branch 'master'
                }
            }
            steps {
                bat '''
                    cd /d C:\\Users\\Tecno\\OneDrive\\Desktop\\web2
                    docker compose down || exit 0
                    '''
            }
        }

        stage('Запуск контейнеров') {
            when {
                anyOf {
                    branch 'dev'
                    branch 'master'
                }
            }
            steps {
                bat 'docker compose up -d'
            }
        }

        stage('Проверка') {
            when {
                anyOf {
                    branch 'dev'
                    branch 'master'
                }
            }
            steps {
                bat 'docker ps'
            }
        }
    }

    post {
        success { echo 'Контейнеры запущены' }
        failure { echo 'Умер(' }
    }
}