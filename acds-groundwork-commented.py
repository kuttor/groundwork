#! /usr/bin/env/python
"""
adcs groundwork

Usage:
  adcs-groundwork.py -h | --help
  adcs-groundwork.py --version
  adcs-groundwork.py --env <env>

Arguments:
          Set environment

Options:
  -e --env ENV  Set environment
  -h --help     Show this screen.
  --version     Show version
"""

__author__  = "Andrew Kuttor "
__email__   = "adcs-akuttor@ucsd.com"
__version__ = "0.1.0"

import boto3
import json
import docopt


# function to create cf stack and opsworks stack, layer, and instance
def create_stack():
    client = boto3.client('cloudformation')

    # opens the cloudformation template and removes newline
    with open("json/template.json", "r") as json_template:
        template = json_template.read().replace('\n', '')

    # opens param file and executes a json decode
    with open("json/params.json", "r") as json_params:
        params = json.load(json_params)

    # change out env variable in param file
    params[0]['ParameterValue'] = env

    # boto3 cloudformation method to create stack
    response = client.create_stack(
        StackName=stack_name,
        TemplateBody=template,
        Parameters=params,
        DisableRollback=False,
        ResourceTypes=[
            'AWS::OpsWorks::*',
        ],
        Tags=[
            {
                'Key': 'some_key',
                'Value': env
            }
        ]
    )

    return response


# updates opsworks stack with custom stack-settings
def update_stack():
    client = boto3.client('opsworks', region_name='us-east-1')

    # opens file and creates it as an object
    with open("json/stack-settings.json", "r") as json_custom:
        custom = json.load(json_custom)

    # updates value of configEnv with environment variable
    custom['configEnv'] = env

    # update stack. Dumps method transforms modded-object to string
    response = client.update_stack(
        StackId=output('StackId'),
        CustomJson=json.dumps(custom)
    )

    return response


# creates instance outside of CF to prevent auto-start
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


# grabs outputs and expresses them as dict key-values for easy retrieval
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
    try:
        # parse arguments, use file docstring as a parameter definition
        arguments = docopt.docopt(__doc__)
        env = arguments['--env']

    # handle invalid options
    except docopt.DocoptExit as e:
        print ("Invalid Command")

    stack_name = "datalake-importer-" + env

    create_stack()
    wait()
    update_stack()
    create_instance()
