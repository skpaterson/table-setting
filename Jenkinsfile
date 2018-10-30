def label = "mypod-${UUID.randomUUID().toString()}"
podTemplate(label: label, containers: [
    containerTemplate(name: 'python27', image: 'gcr.io/spaterson-project/jenkins-python27:latest', ttyEnabled: true, command: 'cat'),
  ]) {

    node(label) {
        stage('Checkout code') {
            checkout scm
        }
        stage('Try and use python image') {
            container('python27') {
                stage('Build a python project') {
                    sh 'pwd'
                    sh 'ls -al'
                    sh 'which pip'
                    sh 'python --version'
                    sh 'pip install -r requirements-dev.txt'
                    sh 'pytest test_app.py'
                }
            }
        }
    }
}