# What Is This?
A simple AWS lambda function which will run a quick audit of Ravello VMs. The 
function is invoked by a timer on AWS.


# What Are The Pre-Reqs?
[lambda-uploader][1] - A utility that helps package and upload Python lambda functions to AWS

```
pip install lambda-uploader
```

# Setup
There needs to be an IAM ["Execution Role"][2] defined to allow our lambda role to execute. This
example uses lambda_s3_monitor. There are 2 sections within `lambda_s3_monitor`.  One sets s3 permissions and the other defines runtime logging.

1. Sign in to the IAM console at https://console.aws.amazon.com/iam/
1. Follow the steps in ["Creating a Role for an AWS Service"][3] in the IAM User Guide to create an IAM role (execution role). As you follow the steps to create a role, note the following:
    1. In Role Name, use a name that is unique within your AWS account (for example, lambda-s3-execution-role).
    1. In Select Role Type, choose AWS Service Roles, and then choose AWS Lambda. This grants the AWS Lambda service permissions to assume the role.
    1. In Attach Policy, choose `AWSLambdaBasicExecutionRole`.
1. Change the `role` line in `lambda.json` to match your new role name and user id

In the same directory as this readme file, run the command
```
make
```

[1]: https://github.com/rackerlabs/lambda-uploader
[2]: https://docs.aws.amazon.com/lambda/latest/dg/intro-permission-model.html#lambda-intro-execution-role
[3]: http://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-service.html
