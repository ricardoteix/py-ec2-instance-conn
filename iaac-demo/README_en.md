[<img src="https://em-content.zobj.net/thumbs/160/openmoji/338/flag-brazil_1f1e7-1f1f7.png" alt="us flag" width="48"/>](./README.md)

# Introduction

This Terraform project allows you to create a minimal infrastructure for testing the EC2 Instance Connect Endpoint.

It will create 1 VPC with 3 private subnets and 3 public subnets. Some security groups and 3 EC2 instances will be created, one for each private subnet, in addition to the EC2 Instance Connect Endpoint instance.

# Terraform

Terraform is a technology used for Infrastructure as Code (IaaC), similar to AWS CloudFormation.

However, with Terraform, it's possible to define infrastructure for other clouds like GCP and Azure.

## Installation

To use Terraform, you need to download the compiled binary file for your system. Visit [https://www.terraform.io/downloads](https://www.terraform.io/downloads).

## Initializing the Repository

You need to initialize Terraform at the root of this project by executing

```
terraform init
```

## Defining Credentials

The Terraform definition file is named main.tf.

This is where we specify how our infrastructure will be set up.

It's important to note that in the provider "aws" block, we define that we're using Terraform with AWS.

```
provider "aws" {
  region = "us-east-1"
  profile = "my-profile"
}
```

Since Terraform automatically creates the entire infrastructure on AWS, permissions are required for this through credentials.

Although it's possible to specify the keys directly within the provider block, this approach is not recommended. Especially since this code is in a Git repository, anyone with access to the repository would have access to the credentials.

A better option is to use an AWS *profile* configured locally.

Here, we're using a profile named **my-project**. To create a profile, execute the following command using the AWS CLI and fill in the prompted parameters.


```
aws configure --profile my-profile
```

## Variables - Additional Configurations

In addition to configuring the profile, you'll need to define some variables.

To avoid exposing sensitive data on Git, such as database passwords, you need to copy the ``terraform.tfvars.example`` file to ``terraform.tfvars``.

In the ``terraform.tfvars`` file, redefine the values of the variables. Note that you'll need to have a domain registered in Route53 if you want to use a domain instead of just accessing via the LoadBalancer's URL.

All possible variables for this file can be seen in the ``variables.tf`` file. Only a few of them were used in the example.

## Applying the Defined Infrastructure

Terraform provides several basic commands to plan, apply, and destroy infrastructure.

When you start applying the infrastructure, Terraform creates the ``terraform.tfstate`` file, which should be preserved and not manually modified.

Through this file, Terraform knows the current state of the infrastructure and can add, modify, or remove resources.

In this repository, we're not versioning this file because it's a shared repository for study purposes. In a real repository, you would likely want to keep this file preserved in Git.

###  Checking What Will Be Created, Removed, or Modified
```
terraform plan
```

###  Applying the Defined Infrastructure
```
terraform apply
```
or, to automatically confirm.
```
terraform apply --auto-approve
```

###  Destroying Your Entire Infrastructure

<font color="red">
  <span><b>CAUTION!</b><br>
  After executing the commands below, you will lose everything specified in your Terraform file (database, EC2, EBS, etc.).</span>
</font>

```
terraform destroy
```
or, to automatically confirm.
```
terraform destroy --auto-approve
```

# Final Considerations

This project is designed for experimentation and studying Terraform. Although it provides the creation of the minimum resources to run the project on AWS, it is not recommended to use this project for deploying workloads in a production environment.

# References

1. [Terraform](https://www.terraform.io/)
