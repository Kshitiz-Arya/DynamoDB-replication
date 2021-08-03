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
        """This method takes in the scope, namespace, table_name and table_replicas and creates the stackset

        Args:
            scope (Construct): This represents cdktf application
            ns (str): This represents the name of the application
            tables (list): list of all the tables
            replicas (list): list of all the table replicas to be created in the formate of [{regionName: region}]
            current_region (str): This represents the current region of the cdktf application
        """        
        super().__init__(scope, ns)
        self.ids = []

        AwsProvider(self, 'Aws', region=current_region)
        self.create_stack(tables, replicas)

    def create_stack(self, table_name: list, table_replicas: list):
        """This method is responsible for creating the stackset of all the tables

        Args:
            table_name (list): list of all the tables
            table_replicas (list): list of all the table replicas to be created in the formate of [{regionName: region}]
        """        

        resources = boto3.resource('dynamodb', region_name=current_region)
        for table in table_name:
            info = resources.Table(table)

            try:
                # get the list of replicas, atrribute and hash key from info
                attributes = [dict(zip(['name', 'type'], list(attribute.values()))) for attribute in info.attribute_definitions]
                hash_key = info.key_schema[0]['AttributeName']

                # extract region_name from old_replicas and add it to updated_replicas
                old_replicas = [] if info.replicas is None else [{'regionName': item['RegionName']} for item in info.replicas if info.replicas]
                updated_replicas = old_replicas + table_replicas
                
                # Create DynamoTable resource
                x = DynamodbTable(self, id=table, name=table, attribute=attributes, hash_key=hash_key, replica=updated_replicas, stream_enabled=True, stream_view_type='NEW_AND_OLD_IMAGES', billing_mode='PAY_PER_REQUEST') # ask for billing_mode 
                self.ids.append((x.id.split('.')[1], table))     # Storing local id to import resources later

            except ClientError as ce:
                if ce.response['Error']['Code'] == 'ResourceNotFoundException':
                    print(f"Table {table} does not exist. Create the table first")
                else:
                    print(f"Unknown exception occurred while querying for the {table} table. Printing full error:")
                    print(ce.response)

app = App()

# Splitting the inuputs into lists, one for the table and one for the table replica
regions = input("Enter a comma seperated list of regions where tables will be replicated to (us-east-1, us-east-2) :- ").split(', ')
tables = input("Enter a comma seperated list of tables to make replica of (Table1, Table2) :- ").split(', ')
current_region = input('Enter the region name where table resides :- ')

# 
replicas =[{'regionName': region} for region in regions] # Converting the replica list into a list of dictionaries with the forrmat {'regionName': region}

stackname = "DynamoDB replication"

stack = MyStack(app, stackname, tables, replicas, current_region)
ids = stack.ids


app.synth()

# Removing the older build directory
shutil.rmtree('build')
os.mkdir(f"build")

# Copying .terraform module and stack config to build directory
shutil.copytree(f'.terraform', './build/.terraform')
shutil.copy(f'cdktf.out/stacks/{stackname}/cdk.tf.json', './build')
shutil.copy('.terraform.lock.hcl', './build/')
os.chdir("./build")

# Initiaing the terraform with configuration
os.system('terraform init')

# importing the resources one by one
for id, table in ids:
    print(f'Importing table {table}')
    os.system(f'terraform import aws_dynamodb_table.{id} {table}')
