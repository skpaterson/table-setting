def pod_label = "mypod-${UUID.randomUUID().toString()}"
pipeline {
  agent {
    kubernetes {
      label pod_label
      yaml """
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: python3
    image: gcr.io/spaterson-project/jenkins-python3:3.7
    command: ['cat']
    tty: true
"""
    }
  }
  stages {
    stage('Checkout code') {
        checkout scm
    }
    container('python3') {
        stage('Build Information') {
            sh 'pwd'
            sh 'ls -al'
            sh 'echo $PATH'
            sh 'ls -al /usr/bin'
        }
        stage('Install python dependencies') {
            sh 'python3.7 -m venv tsenv'
            sh '. tsenv/bin/activate && pip install wheel && pip install setuptools --upgrade && pip install -r requirements-dev.txt && pip list'
        }
        stage('Test python application') {
            sh '. tsenv/bin/activate && pytest -v test_app.py'
        }
    }
  }
  options {
    buildDiscarder logRotator(artifactDaysToKeepStr: '', artifactNumToKeepStr: '', daysToKeepStr: '', numToKeepStr: '10')
  }  
}