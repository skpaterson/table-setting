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
            }
            stage('Install python dependencies') {
                sh 'python3.7 -m venv tsenv'
                sh 'pip install wheel' 
                sh 'pip install setuptools --upgrade'
                sh '. tsenv/bin/activate && pip install -r requirements-dev.txt && pip list'
            }
            stage('Test python application') {
                sh '. tsenv/bin/activate && pytest -v test_app.py'
            }
        }
    }
}