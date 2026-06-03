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
                    /var/jenkins_home/.local/bin/uv sync
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
                      --html=reports/report.html \
                      --self-contained-html
                '''
            }
        }
    }

    post {
        always {
            junit allowEmptyResults: true, testResults: 'reports/junit.xml'

            archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true
        }
    }
}