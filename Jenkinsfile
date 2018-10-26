@Library('jenkins-pipeline-scripts') _

pipeline {
    agent none
    triggers {
        pollSCM('*/3 * * * *')
    }
    options {
        // Keep the 50 most recent builds
        buildDiscarder(logRotator(numToKeepStr:'30'))
    }
    stages {
        stage('Build') {
            agent any
            steps {
                sh 'make docker-image'
            }
        }
        stage('Push image to registry') {
            agent any
            steps {
                pushImageToRegistry (
                    env.BUILD_ID,
                    'webservicejson/mutual'
                )
            }
        }
        stage('Deploy to staging') {
            agent any
            when {
                expression {
                    currentBuild.result == null || currentBuild.result == 'SUCCESS'
                }
            }
            steps {
                sh "mco shell run 'docker pull docker-staging.imio.be/webservicejson/mutual:$BUILD_ID' -I /^staging.imio.be/"
                sh "mco shell run 'systemctl restart webservicejson.service' -I /^staging.imio.be/"
            }
        }
        stage('Deploy to prod') {
            agent any
            when {
                expression {
                    currentBuild.result == null || currentBuild.result == 'SUCCESS'
                }
            }
            steps {
                sh "docker pull docker-staging.imio.be/webservicejson/mutual:$BUILD_ID"
                sh "docker tag docker-staging.imio.be/webservicejson/mutual:$BUILD_ID docker-prod.imio.be/webservicejson/mutual:$BUILD_ID"
                sh "docker tag docker-staging.imio.be/webservicejson/mutual:$BUILD_ID docker-prod.imio.be/webservicejson/mutual:latest"
                sh "docker push docker-prod.imio.be/webservicejson/mutual"
                sh "docker rmi docker-staging.imio.be/webservicejson/mutual:$BUILD_ID"
                sh "docker rmi docker-prod.imio.be/webservicejson/mutual:latest"
                sh "docker rmi docker-prod.imio.be/webservicejson/mutual:$BUILD_ID"
            }
        }
    }
}
