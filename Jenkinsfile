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

        stage('Run unit tests') {
            steps {
                echo 'running unit tests ...'
                sh '''
                    mkdir -p reports

                    /var/jenkins_home/.local/bin/uv run pytest \
                      -v \
                      tests/test_main.py \
                      --junitxml=reports/junit-unit.xml \
                      --alluredir=reports/allure-results \
                      --clean-alluredir
                '''
            }
        }

        stage('Run e2e tests') {
            steps {
                echo 'starting uvicorn and running e2e tests ...'
                sh '''
                    mkdir -p reports

                    /var/jenkins_home/.local/bin/uv run uvicorn main:app \
                      --host 127.0.0.1 \
                      --port 9875 \
                      > reports/server.log 2>&1 &
                    SERVER_PID=$!

                    cleanup() {
                      kill "$SERVER_PID" 2>/dev/null || true
                      wait "$SERVER_PID" 2>/dev/null || true
                    }
                    trap cleanup EXIT

                    for i in $(seq 1 30); do
                      if curl -fsS http://127.0.0.1:9875/health >/dev/null; then
                        break
                      fi

                      if ! kill -0 "$SERVER_PID" 2>/dev/null; then
                        echo 'uvicorn exited before health check passed'
                        cat reports/server.log
                        exit 1
                      fi

                      sleep 1
                    done

                    curl -fsS http://127.0.0.1:9875/health >/dev/null

                    E2E_BASE_URL=http://127.0.0.1:9875 \
                    /var/jenkins_home/.local/bin/uv run pytest \
                      -v \
                      -o addopts= \
                      -m e2e \
                      tests/test_e2e.py \
                      --junitxml=reports/junit-e2e.xml \
                      --alluredir=reports/allure-results
                '''
            }
        }
    }

    post {
        always {
            junit testResults: 'reports/junit-*.xml'

            allure([
                includeProperties: false,
                jdk: '',
                results: [[path: 'reports/allure-results']]
            ])

            archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true
        }
    }
}
