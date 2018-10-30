def label = "mypod-${UUID.randomUUID().toString()}"
podTemplate(label: label, containers: [
    containerTemplate(name: 'python3', image: 'gcr.io/spaterson-project/jenkins-python3:latest', ttyEnabled: true, command: 'cat'),
  ]) {

    node(label) {
        stage('Checkout code') {
            checkout scm
        }
        container('python3') {
            stage('Build Information') {
                sh 'pwd'
                sh 'ls -al'
                sh 'which pip'
                sh 'python3 --version'
            }
            stage('Install python dependencies') {
                sh 'python3 -m venv tsenv'
                sh '. tsenv/bin/activate'
                sh 'pip install -r requirements-dev.txt'
            }
            stage('Test python application') {
                sh 'pytest -v test_app.py'
            }
        }
    }
}