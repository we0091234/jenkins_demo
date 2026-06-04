pipeline {
    agent any

    environment {
        IMAGE_NAME = 'jenkins-demo'
        CONTAINER_NAME = 'jenkins-demo'
        APP_PORT = '9050'
    }

    options {
        disableConcurrentBuilds()
    }

    stages {
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

        stage('Check Docker') {
            steps {
                echo 'checking access to host docker ...'
                sh '''
                    docker version
                    docker info >/dev/null
                '''
            }
        }

        stage('Build image') {
            steps {
                echo 'building application image ...'
                sh '''
                    docker build \
                      --tag "${IMAGE_NAME}:${BUILD_NUMBER}" \
                      .
                '''
            }
        }

        stage('Deploy') {
            when {
                anyOf {
                    branch 'main'
                    expression {
                        env.GIT_BRANCH == 'main' || env.GIT_BRANCH == 'origin/main'
                    }
                }
            }
            steps {
                echo 'deploying latest application image ...'
                sh '''
                    set -eu

                    NEW_IMAGE="${IMAGE_NAME}:${BUILD_NUMBER}"
                    OLD_IMAGE=$(docker inspect \
                      --format='{{.Image}}' \
                      "${CONTAINER_NAME}" 2>/dev/null || true)

                    rollback() {
                      echo 'deployment failed, restoring previous container ...'
                      docker logs "${CONTAINER_NAME}" 2>/dev/null || true
                      docker rm -f "${CONTAINER_NAME}" 2>/dev/null || true

                      if [ -n "${OLD_IMAGE}" ]; then
                        docker run -d \
                          --name "${CONTAINER_NAME}" \
                          --restart unless-stopped \
                          -p "${APP_PORT}:${APP_PORT}" \
                          "${OLD_IMAGE}"
                      else
                        echo 'no previous image is available for rollback'
                      fi
                    }

                    docker rm -f "${CONTAINER_NAME}" 2>/dev/null || true

                    if ! docker run -d \
                      --name "${CONTAINER_NAME}" \
                      --restart unless-stopped \
                      -p "${APP_PORT}:${APP_PORT}" \
                      "${NEW_IMAGE}"; then
                      rollback
                      exit 1
                    fi

                    HEALTHY=false
                    for i in $(seq 1 30); do
                      if docker exec "${CONTAINER_NAME}" python -c \
                        "import urllib.request; urllib.request.urlopen('http://127.0.0.1:${APP_PORT}/health', timeout=2)"; then
                        HEALTHY=true
                        break
                      fi

                      if ! docker inspect "${CONTAINER_NAME}" >/dev/null 2>&1; then
                        break
                      fi

                      sleep 1
                    done

                    if [ "${HEALTHY}" != 'true' ]; then
                      rollback
                      exit 1
                    fi

                    docker tag "${NEW_IMAGE}" "${IMAGE_NAME}:latest"
                    echo "deployed ${NEW_IMAGE} on port ${APP_PORT}"
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
