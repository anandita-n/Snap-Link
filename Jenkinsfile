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
                        catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
                            dir('backend') {
                                powershell 'pip install -r requirements.txt'
                                powershell '''
                                    $ErrorActionPreference = "Stop"
                                    pytest | Tee-Object -FilePath backend_test.log
                                    if ($LASTEXITCODE -ne 0) { throw "pytest failed" }
                                '''
                            }
                        }
                    }
                }

                stage('Frontend') {
                    steps {
                        catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
                            dir('frontend') {
                                powershell 'npm install'
                                script {
                                    def lintFailed = false
                                    try {
                                        powershell '''
                                            $ErrorActionPreference = "Stop"
                                            npm run lint | Tee-Object -FilePath frontend_lint.log
                                            if ($LASTEXITCODE -ne 0) { throw "lint failed" }
                                        '''
                                    } catch (err) {
                                        lintFailed = true
                                        env.FRONTEND_FAILED = 'true'
                                        env.FRONTEND_STAGE_FAILED = 'lint'
                                    }
                                    
                                    try {
                                        powershell '''
                                            $ErrorActionPreference = "Stop"
                                            npm run test | Tee-Object -FilePath frontend_test.log
                                            if ($LASTEXITCODE -ne 0) { throw "test failed" }
                                        '''
                                    } catch (err) {
                                        env.FRONTEND_FAILED = 'true'
                                        if (!lintFailed) {
                                            env.FRONTEND_STAGE_FAILED = 'test'
                                        }
                                    }

                                    if (env.FRONTEND_FAILED == 'true') {
                                        error "Frontend step failed"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
