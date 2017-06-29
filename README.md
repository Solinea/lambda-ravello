# What Are The Pre-Reqs?
[lambda-uploader][1] - A utility that helps package and upload Python lambda functions to AWS

```
pip install lambda-uploader
```

# Setup
There needs to be an IAM ["Execution Role"][2] defined to allow our lambda role to execute. This
example uses lambda_s3_monitor. There are 2 sections within `lambda_s3_monitor`.  One sets s3 permissions and the other defines runtime logging.

1. Follow the steps in Creating a Role for an AWS Service (AWS Management Console) in the IAM User Guide to create an IAM role (execution role). As you follow the steps to create a role, note the following:
  1. In Role Name, use a name that is unique within your AWS account (for example, lambda-s3-execution-role).
  1. In Select Role Type, choose AWS Service Roles, and then choose AWS Lambda. This grants the AWS Lambda service permissions to assume the role.
  1. In Attach Policy, choose `AWSLambdaBasicExecutionRole`.
  1. Change the `role` line in `lambda.json` to match your new role name and user id

In the same directory as this readme file, run command
```
make
```

[1]: https://github.com/rackerlabs/lambda-uploader
[2]: https://docs.aws.amazon.com/lambda/latest/dg/intro-permission-model.html#lambda-intro-execution-role
