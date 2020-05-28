module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "vpc"
  cidr = "10.0.0.0/16"

  azs             = ["eu-west-1a", "eu-west-1b", "eu-west-1c"]
  public_subnets  = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}
module "db" {
  source  = "terraform-aws-modules/rds-aurora/aws"

  name                            = "db"

  engine                          = "aurora-postgresql"
  engine_version                  = "11.6"

  vpc_id                          = module.vpc.vpc_id
  subnets                         = module.vpc.public_subnets

  replica_count                   = 1
//  allowed_security_groups         = ["sg-12345678"]
  allowed_cidr_blocks             = ["0.0.0.0/0"]
  instance_type                   = "db.t2.micro"
  storage_encrypted               = true
  apply_immediately               = true
//  monitoring_interval             = 10

//  db_parameter_group_name         = "default"
//  db_cluster_parameter_group_name = "default"
}
