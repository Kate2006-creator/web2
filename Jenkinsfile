pipeline {
    agent any

    environment {
        DOCKER_REPO = 'kate34534534/web2-app'

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
                    bat 'docker login -u %DOCKER_USER% -p %DOCKER_PASS%'
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
                bat """
                    docker build -t ${DOCKER_REPO}:backend .
                    docker build -t ${DOCKER_REPO}:frontend ./client
                """
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
                bat """
                    docker push ${DOCKER_REPO}:backend
                    docker push ${DOCKER_REPO}:frontend
                """
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