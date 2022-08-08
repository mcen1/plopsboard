@Library("shared-pipeline-library") _

node{
  properties([[$class: 'JiraProjectProperty'], buildDiscarder(logRotator(artifactDaysToKeepStr: '', artifactNumToKeepStr: '', daysToKeepStr: '', numToKeepStr: '20'))])
  
  checkout scm
  imageName = "/gcd-linux/gpodash"
  buildOptions = " --no-cache --pull --squash -t "

  buildAndDeployDkrImage(imageName, buildOptions)
}
