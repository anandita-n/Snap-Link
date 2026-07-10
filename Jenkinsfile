pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Test and Lint') {
            parallel {
                stage('Backend') {
                    steps {
                        script {
                            catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
                                dir('backend') {
                                    sh 'pip install -r requirements.txt'
                                    sh 'set -o pipefail; pytest 2>&1 | tee backend_test.log'
                                }
                            }
                        }
                    }
                }

                stage('Frontend') {
                    steps {
                        script {
                            catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
                                dir('frontend') {
                                    sh 'npm install'
                                    sh 'set -o pipefail; npm run lint 2>&1 | tee frontend_lint.log'
                                    sh 'set -o pipefail; npm run test 2>&1 | tee frontend_test.log'
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
