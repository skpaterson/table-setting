def pod_label = "table-setting-${UUID.randomUUID().toString()}"
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
    image: gcr.io/spaterson-project/jenkins-python3-b2
    command: ['cat']
    tty: true
"""
    }
  }
  stages {
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
                sh '. tsenv/bin/activate && pip install wheel && pip install setuptools --upgrade && pip install --upgrade pip && pip install -r requirements-dev.txt && pip list'
            }
        }
    }
    stage('Test python application') {
        steps {
            container('python3') {
                sh '. tsenv/bin/activate && pytest'
            }
        }
    }
  }
  triggers {
    cron 'H 8 * * 1-5'
  }
  post {
    success {
        slackSend color: 'good', message: "The pipeline ${currentBuild.fullDisplayName} completed successfully. <${env.BUILD_URL}|Details here>."
        publishHTML([allowMissing: false, alwaysLinkToLastBuild: false, keepAll: true, reportDir: 'coverage_html', reportFiles: 'index.html', reportName: 'Coverage Report', reportTitles: ''])
    }
    failure {
        slackSend color: 'danger', message: "Pipeline failure ${currentBuild.fullDisplayName}. Please <${env.BUILD_URL}|resolve issues here>."
    }
  }
  options {
    buildDiscarder logRotator(artifactDaysToKeepStr: '', artifactNumToKeepStr: '', daysToKeepStr: '', numToKeepStr: '10')
  }  
}
