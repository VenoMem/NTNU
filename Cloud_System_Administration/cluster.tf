data "aws_eks_cluster" "portfolio-cluster" {
    name = module.p-cluster.cluster_id
}

data "aws_eks_cluster_auth" "portfolio-cluster" {
    name = module.p-cluster.cluster_id
}

provider "kubernetes" {
    host                   = data.aws_eks_cluster.portfolio-cluster.endpoint
    cluster_ca_certificate = base64decode(data.aws_eks_cluster.portfolio-cluster.certificate_authority.0.data)
    token                  = data.aws_eks_cluster_auth.portfolio-cluster.token
}

module "p-cluster" {
    source = "terraform-aws-modules/eks/aws"
    cluster_name = "portfolio-cluster"
    cluster_version="1.21"
    subnets = [aws_subnet.portfolio-subnet1.id,aws_subnet.portfolio-subnet2.id]
    vpc_id=aws_vpc.portfolio-vpc.id

    worker_groups = [
        {
            name                 = "portfolio-worker-group-1"
            instance_type        = "t2.micro"
            asg_min_size         = 1
            asg_desired_capacity = 3
            asg_max_size         = 5
            additional_security_group_ids = [aws_security_group.allow-web-traffic-sg.id]
        }
    ]
}