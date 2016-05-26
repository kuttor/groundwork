#!/usr/bin/env/python
"""
adcs groundwork

Usage:
    adcs-groundwork.py <study>
    adcs-groundwork.py [ -h | --help | --version ]

Options:
    -d --dryrun           Simulates environment creation
    -h --help             Show this menu
    --version             Show version

Examples:
    adcs-groundwork.py pita-test --dryrun
"""

__author__  = "Andrew Kuttor"
__email__   = "adcs-akuttor@ucsd.edu"
__version__ = "0.1.0"

from boto3 import resource
from boto3 import client
from docopt import docopt, DocoptExit
import json


def main():
    try:
        # parse arguments, use file docstring as a parameter definition
        arguments = docopt.docopt(__doc__)
        study = arguments['<study_name>']

    # handle invalid options
    except docopt.DocoptExit as e:
        print ("Invalid Command")

    create_stack()
    wait()
    update_stack()
    create_instance()


def create_vpc():
    ec2 = resource('ec2')

    vpc = ec2.Vpc(
        id='Name_ID',
        CidrBlock='10.0.0.0/16',
        vpc_id="string"
    )

    subnet = ec2.Subnet(
        id='ID',
        availability_zone='string',
        cidr_block='string',
        subnet_id='',
        vpc_id='string',
        state='string'
    )

    gateway = ec2.InternetGateway(
        id='id',
        attachments='string',
        internet_gateway_id='string',
        tags='string'
    )

    response = internet_gateway.attach_to_vpc(
        DryRun=True|False,
        VpcId='string'
    )

    route = ec2.Route(
        route_table_id='string',
        destination_cidr_block='string',
        gateway_id='string',

    )


# creates an opsworks stack
def create_stack(study_name):
    cf = client('cloudformation')

    with open("json/template.json", "r") as json_template:
        template = json_template.read().replace('\n', '')
    with open("json/params.json", "r") as json_params:
        params = json.load(json_params)

    env = params[0]['ParameterValue']

    response = cf.create_stack(
        StackName=study_name,
        TemplateBody=template,
        Parameters=params,
        DisableRollback=False,
        ResourceTypes=['AWS::OpsWorks::*'],
        Tags=[{'Key': 'some_key','Value': study_name}]
    )
    return response


def update_stack():
    client = boto3.client('opsworks', region_name='us-east-1')
    with open("json/stack-settings.json", "r") as json_custom:
        custom = json.load(json_custom)
    env = custom['configEnv']
    response = client.update_stack(
        StackId=output('StackId'),
        CustomJson=json.dumps(custom)
    )
    return response


def create_instance():
    client = boto3.client('opsworks', region_name='us-east-1')
    response = client.create_instance(
        StackId=output('StackId'),
        LayerIds=[output('some_layer')],
        InstanceType='t2.medium',
        Os='Custom',
        AmiId='some_ami'
    )
    return response


# converts cf outputs to dict-type
def output(output_key):
    client = boto3.client('cloudformation')
    response = client.describe_stacks(StackName=stack_name)

    outputs = response['Stacks'][0]['Outputs']
    params = {}

    for i in outputs:
        params[i['OutputKey']] = i['OutputValue']
    return params[output_key]


# waiter for initial stack
def wait():
    client = boto3.client('cloudformation')
    waiter = client.get_waiter('stack_create_complete')
    waiter.wait(StackName=stack_name)


if __name__ == "__main__":
    main()
