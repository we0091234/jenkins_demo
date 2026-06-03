pipeline {
    agent any

    stages {
        stage('Check out') {
            steps {
                echo 'checking out code ...'

                git branch: 'main',
                    url: 'git@github.com:we0091234/jenkins_demo.git'
            }
        }

        stage('Install dependencies') {
            steps {
                echo 'installing dependencies with uv ...'
                sh '''
                    /var/jenkins_home/.local/bin/uv sync --dev
                '''
            }
        }

        stage('Run tests') {
            steps {
                echo 'running pytest ...'
                sh '''
                    mkdir -p reports

                    /var/jenkins_home/.local/bin/uv run pytest \
                      -v \
                      --junitxml=reports/junit.xml \
                      --alluredir=reports/allure-results \
                      --clean-alluredir
                '''
            }
        }
    }

    post {
        always {
            junit testResults: 'reports/junit.xml'

            allure([
                includeProperties: false,
                jdk: '',
                results: [[path: 'reports/allure-results']]
            ])

            archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true
        }
    }
}
