pipeline {
    agent any
    options { disableConcurrentBuilds(); timeout(time: 15, unit: 'MINUTES'); buildDiscarder(logRotator(numToKeepStr: '20')) }
    parameters {
        string(name: 'PROJECT_DIR', defaultValue: '', description: 'Ruta del checkout local; vacio usa el workspace SCM')
        string(name: 'PYTHON_EXE', defaultValue: 'python', description: 'Python 3.12 con dependencias instaladas')
        string(name: 'CHROMEDRIVER_EXE', defaultValue: '', description: 'ChromeDriver compatible; vacio usa Selenium Manager')
        booleanParam(name: 'MOSTRAR_NAVEGADOR', defaultValue: true, description: 'Mostrar Chrome durante los recorridos Selenium en este equipo')
        booleanParam(name: 'FORZAR_FALLO', defaultValue: false, description: 'Ensayo negativo: provocar un fallo y bloquear promocion')
    }
    environment { PYTHONUTF8 = '1' }
    stages {
        stage('Identificar version') {
            steps {
                script {
                    env.DEMO_ROOT = params.PROJECT_DIR?.trim() ?: pwd()
                    env.REPORT_DIR = 'reports/build-' + env.BUILD_NUMBER
                    env.DEMO_PYTHON = params.PYTHON_EXE ?: 'python'
                    ws(env.DEMO_ROOT) {
                        bat 'git rev-parse HEAD'
                        bat 'if not exist "%REPORT_DIR%" mkdir "%REPORT_DIR%"'
                        bat 'git rev-parse HEAD > "%REPORT_DIR%\\source-sha.txt"'
                        bat 'git diff --binary > "%REPORT_DIR%\\working-tree.patch"'
                    }
                }
            }
        }
        stage('Regresion API sprint 3 / Azure 9') {
            steps { ws(env.DEMO_ROOT) { dir('backend/api_hospital') {
                bat '"%DEMO_PYTHON%" -m pytest tests/test_sprint9_uat_readiness.py tests/test_sprint9_jesus.py tests/test_sprint9_zahid.py tests/test_uat_clinical_dates.py -v -p no:cacheprovider --basetemp=../../%REPORT_DIR%/tmp-api --junitxml=../../%REPORT_DIR%/api.xml'
            } } }
        }
        stage('Regresion web de Joel') {
            steps { ws(env.DEMO_ROOT) { dir('frontend/clinica-web-react') {
                bat 'call npm test -- src/pages/spark/__tests__/Sprint9Joel.test.jsx src/tests/uat-history-timezone.test.js --reporter=default --reporter=junit --outputFile=../../%REPORT_DIR%/web.xml'
            } } }
        }
        stage('OAT salud y recuperacion') {
            steps { ws(env.DEMO_ROOT) { dir('backend/api_hospital') {
                bat '"%DEMO_PYTHON%" -m pytest tests/test_oat_joel.py tests/test_oat_http_joel.py -v -p no:cacheprovider --basetemp=../../%REPORT_DIR%/tmp-oat --junitxml=../../%REPORT_DIR%/oat.xml'
            } } }
        }
        stage('Selenium recorridos del usuario') {
            steps { ws(env.DEMO_ROOT) { withEnv([
                "CHROMEDRIVER_EXE=${params.CHROMEDRIVER_EXE ?: ''}",
                "INEO_SHOW_BROWSER=${params.MOSTRAR_NAVEGADOR}",
                "INEO_SCREENSHOT_DIR=${env.DEMO_ROOT}/${env.REPORT_DIR}/screenshots"
            ]) {
                bat '"%DEMO_PYTHON%" -m pytest ci/selenium -v -p no:cacheprovider --basetemp=%REPORT_DIR%/tmp-selenium --junitxml=%REPORT_DIR%/selenium.xml'
            } } }
        }
        stage('Ensayo de bloqueo') {
            steps { ws(env.DEMO_ROOT) { withEnv(["INEO_FORCE_FAILURE=${params.FORZAR_FALLO}"]) {
                bat '"%DEMO_PYTHON%" -m pytest ci/test_gate_demo.py -v -p no:cacheprovider --junitxml=%REPORT_DIR%/gate.xml'
            } } }
        }
        stage('Promocion de demostracion') {
            steps { ws(env.DEMO_ROOT) { writeFile file: env.REPORT_DIR + '/promotion.txt', text: 'Controles aprobados. Candidato SOLO de demostracion local; no despliegue ni aceptacion UAT.\n' } }
        }
    }
    post {
        always {
            script {
                if (env.DEMO_ROOT) { ws(env.DEMO_ROOT) {
                    junit testResults: env.REPORT_DIR + '/*.xml', allowEmptyResults: false
                    archiveArtifacts artifacts: env.REPORT_DIR + '/*.xml,' + env.REPORT_DIR + '/*.txt,' + env.REPORT_DIR + '/*.patch,' + env.REPORT_DIR + '/screenshots/*', allowEmptyArchive: false
                } }
            }
        }
    }
}
