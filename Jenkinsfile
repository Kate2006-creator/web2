pipeline {
    #added
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
                venv\\Scripts\\activate
                pip install -r requirements.txt
                pytest --maxfail=1 --disable-warnings -q --junitxml=report.xml
            '''
            }
        }

        stage('Run tests') {
            steps {
                sh '''
                    . venv/bin/activate
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
            echo ' CI прошёл успешно. Для ветки main это означает готовность к поставке (CD).'
        }
        failure {
            echo 'CI упал. Проверьте вывод pytest.'
        }
    }
}