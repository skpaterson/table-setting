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
        steps  {
            checkout scm
        }
    }
    stage('Build Information') {
        steps {
            container('python3') {
                sh 'pwd'
                sh 'ls -al'
                sh 'echo $PATH'
            }
        }
    }
    stage('Install python dependencies') {
        steps {
            container('python3') {
                sh 'python3.7 -m venv tsenv'
                sh '. tsenv/bin/activate && pip install wheel && pip install setuptools --upgrade && pip install -r requirements-dev.txt && pip list'
            }
        }
    }
    stage('Test python application') {
        steps {
            container('python3') {
                sh '. tsenv/bin/activate && pytest -v test_app.py'
            }
        }
    }
  }
  options {
    buildDiscarder logRotator(artifactDaysToKeepStr: '', artifactNumToKeepStr: '', daysToKeepStr: '', numToKeepStr: '10')
  }  
}