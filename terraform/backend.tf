terraform {
  backend "s3" {
    bucket         = "whatjacketdoineed-tf-state"
    key            = "terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "whatjacketdoineed-locks"
    encrypt        = true
  }
}