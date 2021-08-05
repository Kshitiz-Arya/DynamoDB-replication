# Getting Started with this Project

## Prerequisites

- [Terraform](https://www.terraform.io/downloads.html) >= v0.12
- [Node.js](https://nodejs.org) >= v12.16
- [Python](https://www.python.org/downloads/) >= v3.7

### Install CDK for Terraform CLI

Install with [Homebrew](https://brew.sh):

```bash
brew install cdktf
```

Or install with `npm` (comes with [Node.js](https://nodejs.org)):

```bash
npm install -g cdktf-cli
```

### Install Pipenv

Install with [Homebrew](https://brew.sh):

```bash
$ brew install pipenv
```

You can install Pipenv by visiting the [website](https://pipenv.pypa.io/en/latest/).

## Clone the Project Repository

Using GitHub CLI

```bash
gh repo clone Kshitiz-Arya/DynamoDB-replication
```

Using git

```bash
git clone https://github.com/Kshitiz-Arya/DynamoDB-replication.git
```

## Install project dependencies

```bash
cd DynamoDB-replication
pipenv install
```

Generate CDK for Terraform constructs for Terraform providers and modules used in the project.

```bash
cdktf get
```


## CDK for Terraform Application

You can now edit the `main.py` file if you want to modify any code.

```bash
vim main.py
```

```python
#!/usr/bin/env python
import os
import shutil

import boto3
from botocore.exceptions import ClientError
from cdktf import App, TerraformStack
from constructs import Construct

from imports.aws import AwsProvider, DynamodbTable


class MyStack(TerraformStack):
    def __init__(self, scope: Construct, ns: str, tables, replicas, current_region):
      
        super().__init__(scope, ns)
        self.ids = []

        AwsProvider(self, 'Aws', region=current_region)
        self.create_stack(tables, replicas)
```



## Compile and generate Terraform configuration

When you are ready you can run the `main.py` file to generate Terraform JSON configuration for the application.

```bash
pipenv run python main.py
```

> Now enter the comma seperated list of regions, table names and current region

This command will generate a directory called `build`. This directory contains the Terraform JSON configuration for
the application.

```bash
cd build
```

Terraform AWS provider and instance expressed as Terraform JSON configuration.

```json
cat cdk.tf.json
{
  "terraform": {
    "required_providers": {
      "aws": "~> 2.0"
    }
  },
  "provider": {
    "aws": [
      {
        "region": "us-east-1"
      }
    ]
  },
  "resource": {
    "aws_dynamodb_table": {
      "DynamoDBreplication_example_table": {
        "billing_mode": "PAY_PER_REQUEST",
        "hash_key": "example_key",
        "name": "example_table",
        "stream_enabled": true,
        "stream_view_type": "NEW_AND_OLD_IMAGES",
        "attribute": [
          {
            "name": "example_key",
            "type": "S"
          }
        ],
        "replica": [
          {
            "region_name": "ap-south-1"
          }
        ]
      }
    }
  }
}
```


## Deploy Application

> Note: You can use Terraform commands like `terraform init`, `terraform plan`, and `terraform apply` with the generated


```bash
terraform apply
```

This command will ask for confirmation on a generated plan and then deploy the application.

```bash
aws_dynamodb_table.DynamoDBreplication_exampleTable: Refreshing state... [id=exampleTable]

Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with
the following symbols:
  ~ update in-place

Terraform will perform the following actions:

  # aws_dynamodb_table.DynamoDBreplication_exampleTable will be updated in-place
  ~ resource "aws_dynamodb_table" "DynamoDBreplication_exampleTable" {
        id               = "example_table"
        name             = "example_table"
        tags             = {}
        # (10 unchanged attributes hidden)



      - replica {
          - region_name = "ap-south-1" -> null
        }
      + replica {
          + kms_key_arn = (known after apply)
          + region_name = "ap-northeast-1"
        }
      + replica {
          + kms_key_arn = (known after apply)
          + region_name = "ap-south-1"
        }
      + replica {
          + kms_key_arn = (known after apply)
          + region_name = "eu-west-2"
        }


        # (4 unchanged blocks hidden)
    }

  
Plan: 0 to add, 1 to change, 0 to destroy.

Do you want to perform these actions?
  Terraform will perform the actions described above.
  Only 'yes' will be accepted to approve.

  Enter a value: 
```
