pipeline {
    agent any

    environment {
        // Toggle variables can be overridden at the pipeline/system level if needed,
        // but by default we run tests normally.
        TOGGLE_TEST_FAILURE = 'true'
        VITE_TOGGLE_TEST_FAILURE = 'false'
    }

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
                                script {
                                    try {
                                        powershell '''
                                            $ErrorActionPreference = "Stop"
                                            pytest | Tee-Object -FilePath backend_test.log
                                            if ($LASTEXITCODE -ne 0) { throw "pytest failed" }
                                        '''
                                    } catch (err) {
                                        env.BACKEND_FAILED = 'true'
                                        env.BACKEND_STAGE_FAILED = 'test'
                                        error "Backend tests failed"
                                    }
                                }
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

        stage('AI Analysis') {
            when {
                expression { currentBuild.result == 'FAILURE' }
            }
            steps {
                withCredentials([string(credentialsId: 'gemini-api-key', variable: 'GEMINI_API_KEY')]) {
                    script {
                        def args = []
                        if (env.BACKEND_FAILED == 'true') {
                            args << "--failure backend:${env.BACKEND_STAGE_FAILED}:backend/backend_test.log"
                        }
                        if (env.FRONTEND_FAILED == 'true') {
                            if (env.FRONTEND_STAGE_FAILED == 'lint') {
                                args << "--failure frontend:lint:frontend/frontend_lint.log"
                            } else {
                                args << "--failure frontend:test:frontend/frontend_test.log"
                            }
                        }
                        
                        echo "Triggering Gemini AI Analysis with arguments: ${args.join(' ')}"
                        
                        try {
                            powershell "python scripts/analyze_failure.py ${args.join(' ')}"
                        } catch (err) {
                            echo "AI Triage analysis encountered an execution error: ${err.message}"
                        }
                    }
                }
            }
        }

        stage('Report') {
            steps {
                script {
                    if (fileExists('triage_report.json')) {
                        def reportText = readFile('triage_report.json')
                        echo "=== Build Triage Report ===\n${reportText}"
                        archiveArtifacts artifacts: 'triage_report.json', allowEmptyArchive: true
                    } else {
                        echo "No triage report found to display or archive."
                    }
                }
            }
        }
    }
}
