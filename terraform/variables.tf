variable "region" {
  default = "eu-central-1"
}

variable "ami" {
  # Ubuntu 24.04 LTS eu-central-1
  default = "ami-0084a47cc718c111a"
}

variable "instance_type" {
  default = "t3.micro"
}
