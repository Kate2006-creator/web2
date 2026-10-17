pipeline {
    agent any

    environment {
        DOCKER_HUB_USER = 'kate34534534'
        DOCKER_HUB_CREDS = 'docker-hub'
        BACKEND_IMAGE = "${DOCKER_HUB_USER}/web2-backend"
        FRONTEND_IMAGE = "${DOCKER_HUB_USER}/web2-frontend"
    }

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

        stage('Логин в Docker Hub') {
            when {
                anyOf { branch 'dev'; branch 'master' }
            }
            steps {
                withCredentials([usernamePassword(credentialsId: 'docker-hub', passwordVariable: 'DOCKER_PASS', usernameVariable: 'DOCKER_USER')]) {
                    bat 'echo %DOCKER_PASS% | docker login -u %DOCKER_USER% --password-stdin'
                }
            }
        }

        stage('Сборка и тегирование образов') {
            when {
                anyOf {
                    branch 'dev'
                    branch 'master'
                }
            }
            steps {
                bat '''
                    docker build -t kate34534534/web2-backend:latest .
                    docker build -t kate34534534/web2-frontend:latest ./client
                '''
            }
        }

        stage('Пуш в Docker Hub') {
            when {
                anyOf {
                    branch 'dev'
                    branch 'master'
                }
            }
            steps {
                bat '''
                    docker push kate34534534/web2-backend:latest
                    docker push kate34534534/web2-frontend:latest
                '''
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