terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

# SSH Key Pair
resource "aws_key_pair" "pastebin" {
  key_name   = "pastebin-key"
  public_key = file("~/.ssh/pastebin.pub")
}

# Security Group
resource "aws_security_group" "pastebin" {
  name        = "pastebin-sg"
  description = "Pastebin security group"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "pastebin-sg"
  }
}

# Elastic IP
resource "aws_eip" "pastebin" {
  instance = aws_instance.pastebin.id
  domain   = "vpc"

  tags = {
    Name = "pastebin-eip"
  }
}

# EC2 Instance
resource "aws_instance" "pastebin" {
  ami                    = var.ami
  instance_type          = var.instance_type
  key_name               = aws_key_pair.pastebin.key_name
  vpc_security_group_ids = [aws_security_group.pastebin.id]
  user_data              = file("userdata.sh")

  tags = {
    Name = "pastebin-server"
  }
}
