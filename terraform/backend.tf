# Backend.tf

terraform {
  backend "s3" {
    # Use the unique bucket name you just created
    bucket         = "linkshrink-microservices-tfstate"
    # This is the path/filename for the state file inside the bucket
    key            = "global/terraform.tfstate"
    region         = "us-east-2"
  }
}