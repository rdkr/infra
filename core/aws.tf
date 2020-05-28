module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "vpc"
  cidr = "10.0.0.0/16"

  azs             = ["eu-west-1a", "eu-west-1b", "eu-west-1c"]
  public_subnets  = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]

  enable_dns_hostnames = true
  enable_dns_support   = true
}

resource "aws_security_group" "db" {
  name        = "db"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}


module "db" {
  source  = "terraform-aws-modules/rds/aws"

  identifier = "db"

  engine            = "postgres"
  engine_version    = "12.2"
  instance_class    = "db.t2.micro"
  allocated_storage = 5
  storage_encrypted = false

  username = "root"
  password = var.HERMES_DB_PW
  port     = "5432"

  vpc_security_group_ids = [aws_security_group.db.id]

  maintenance_window = "Mon:00:00-Mon:03:00"
  backup_window      = "03:00-06:00"

  # disable backups to create DB faster
  backup_retention_period = 0

  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]

  # DB subnet group
  subnet_ids = module.vpc.public_subnets

  # DB parameter group
  family = "postgres12"

  # DB option group
  major_engine_version = "12"

  # Snapshot name upon DB deletion
  final_snapshot_identifier = "db"

  # Database Deletion Protection
  deletion_protection = false

  publicly_accessible = true
}

provider "postgresql" {
  host            = module.db.this_db_instance_address
  port            = 5432
  database        = "postgres"
  username        = "root"
  password        = var.HERMES_DB_PW
  sslmode         = "require"
  connect_timeout = 15
}

resource "postgresql_database" "hermes" {
  name              = "hermes"
}
