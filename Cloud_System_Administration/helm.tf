provider "helm" {
  kubernetes {
    host                   = data.aws_eks_cluster.portfolio-cluster.endpoint
    cluster_ca_certificate = base64decode(data.aws_eks_cluster.portfolio-cluster.certificate_authority.0.data)
    exec {
      api_version = "client.authentication.k8s.io/v1alpha1"
      args        = ["eks", "get-token", "--cluster-name", data.aws_eks_cluster.portfolio-cluster.name]
      command     = "aws"
    }
  }
}

resource "helm_release" "jenkins" {
  name       = "jenkins"
  repository = "https://charts.jenkins.io"
  chart      = "jenkins"

  values = [
    "${file("jenkins-parameters.yaml")}"
  ]

  set_sensitive {
    name  = "controller.adminUser"
    value = "admin"
  }
  set_sensitive {
    name = "controller.adminPassword"
    value = "root"
  }
  set_sensitive {
    name = "adminPassword"
    value = "root"
  }
}