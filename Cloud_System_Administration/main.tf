variable "acces_key_string" {}
variable "secret_key_string" {}

provider "aws" {
    access_key = var.acces_key_string
    secret_key = var.secret_key_string
    region     = "us-east-1"
}

resource "aws_vpc" "portfolio-vpc" {
    cidr_block           = "10.0.0.0/16"
    enable_dns_hostnames = true
    enable_dns_support   = true

    tags = {
        Name = "portfolio development"
    }
}

resource "aws_subnet" "portfolio-subnet1" {
    vpc_id                  = aws_vpc.portfolio-vpc.id
    cidr_block              = "10.0.1.0/24"
    availability_zone       = "us-east-1a"
    map_public_ip_on_launch = true

    tags = {
        Name = "portfolio subnet 1"
    }
}

resource "aws_subnet" "portfolio-subnet2" {
    vpc_id                  = aws_vpc.portfolio-vpc.id
    cidr_block              = "10.0.2.0/24"
    availability_zone       = "us-east-1b"
    map_public_ip_on_launch = true

    tags = {
        Name = "portfolio subnet 2"
    }
}

resource "aws_internet_gateway" "portfolio-gateway" {
    vpc_id = aws_vpc.portfolio-vpc.id
}

resource "aws_route_table" "portfolio-route_table" {
    vpc_id = aws_vpc.portfolio-vpc.id
    
    route = [ {
      cidr_block = "0.0.0.0/0"
      gateway_id = aws_internet_gateway.portfolio-gateway.id

      egress_only_gateway_id     = null
      ipv6_cidr_block            = null
      carrier_gateway_id         = null
      destination_prefix_list_id = null
      instance_id                = null
      local_gateway_id           = null
      nat_gateway_id             = null
      network_interface_id       = null
      transit_gateway_id         = null
      vpc_endpoint_id            = null
      vpc_peering_connection_id  = null
    } ]
    
    tags = {
      Name = "portfolio routetable"
    }
}

resource "aws_route_table_association" "a-sub1" {
    subnet_id      = aws_subnet.portfolio-subnet1.id
    route_table_id = aws_route_table.portfolio-route_table.id
}

resource "aws_route_table_association" "a-sub2" {
    subnet_id      = aws_subnet.portfolio-subnet2.id
    route_table_id = aws_route_table.portfolio-route_table.id
}

resource "aws_security_group" "allow-web-traffic-sg" {
    vpc_id = aws_vpc.portfolio-vpc.id

    ingress = [ {
      description = "SSH"
      from_port   = 22
      to_port     = 22
      protocol    = "tcp"
      cidr_blocks = [ "0.0.0.0/0" ]

      ipv6_cidr_blocks = null
      prefix_list_ids  = null
      security_groups  = null
      self             = null
    },
    {
      description = "HTTP"
      from_port   = 80
      to_port     = 80
      protocol    = "tcp"
      cidr_blocks = [ "0.0.0.0/0" ]

      ipv6_cidr_blocks = null
      prefix_list_ids  = null
      security_groups  = null
      self             = null
    },
    {
      description = "HTTPS"
      from_port   = 443
      to_port     = 443
      protocol    = "tcp"
      cidr_blocks = [ "0.0.0.0/0" ]

      ipv6_cidr_blocks = null
      prefix_list_ids  = null
      security_groups  = null
      self             = null
    } ]

    egress = [ {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = [ "0.0.0.0/0" ]

    description      = null
    ipv6_cidr_blocks = null
    prefix_list_ids  = null
    security_groups  = null
    self             = null
    } ]

    tags = {
      Name = "allow web traffic"
    }
}

resource "aws_network_interface" "portfolio-interface" {
    subnet_id       = aws_subnet.portfolio-subnet1.id
    private_ips     = ["10.0.1.30"]
    security_groups = [aws_security_group.allow-web-traffic-sg.id]
}

resource "aws_eip" "one" {
    vpc                       = true
    network_interface         = aws_network_interface.portfolio-interface.id
    associate_with_private_ip = "10.0.1.30"
    depends_on                = [aws_internet_gateway.portfolio-gateway]
}