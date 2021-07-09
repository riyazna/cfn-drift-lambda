import os
import boto3
import json
from datetime import date

cfn = boto3.client('cloudformation')
sns = boto3.client('sns')
sts = boto3.client('sts')
account_id = sts.get_caller_identity().get('Account')
region = boto3.session.Session().region_name
today = date.today().strftime("%d/%m/%Y")
arn = 'arn:aws:sns:eu-west-1:238361238669:MyDriftInfoLambda'
stack_list = []

def lambda_handler(event, context):
    response = cfn.list_stacks(StackStatusFilter=['CREATE_COMPLETE','UPDATE_COMPLETE'])
    stack_summary=response.get('StackSummaries')
    message = "Drift Information for " + account_id + " as of " + today + ".\n"
    for stack in stack_summary:
        drift_status=(stack['DriftInformation']).get('StackDriftStatus')
        if drift_status == 'DRIFTED':
            stack_list.append(stack['StackName'])
    if bool(stack_list):
        message += "Drifted Stacks Are : " + str(stack_list)
    else:
        message += "There are no Drifted stacks"

    sent = sns.publish(
        TargetArn= arn,
        Message=json.dumps({'default': json.dumps(message)}),
        MessageStructure='json'
        )    
