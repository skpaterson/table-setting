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
                sh 'which pip3'
                sh 'python3 --version'
            }
            stage('Install python dependencies') {
                sh 'pip3 install wheel'
                sh 'pip3 install setuptools --upgrade'
                sh 'python3 -m venv tsenv'
                sh '. tsenv/bin/activate && pip install -r requirements-dev.txt && pip list'
            }
            stage('Test python application') {
                sh '. tsenv/bin/activate && pytest -v test_app.py'
            }
        }
    }
}