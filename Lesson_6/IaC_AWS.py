import pandas as pd
import boto3
import json
import configparser
from botocore.exceptions import ClientError
from botocore import exceptions
#load_ext sql

config = configparser.ConfigParser()
config.read_file(open('dwh.cfg'))

### IMPORT CONFIGS ###

KEY                     = config.get('AWS', 'KEY')
SECRET                  = config.get('AWS', 'SECRET')

DWH_CLUSTER_TYPE        = config.get('DWH', 'DWH_CLUSTER_TYPE')
DWH_NUM_NODES           = config.get('DWH', 'DWH_NUM_NODES')
DWH_NODE_TYPE           = config.get('DWH', 'DWH_NODE_TYPE')

DWH_CLUSTER_IDENTIFIER  = config.get('DWH', 'DWH_CLUSTER_IDENTIFIER')
DWH_DB                  = config.get('DWH', 'DWH_DB')
DWH_DB_USER             = config.get('DWH', 'DWH_DB_USER')
DWH_DB_PASSWORD         = config.get('DWH', 'DWH_DB_PASSWORD')
DWH_PORT                = config.get('DWH', 'DWH_PORT')

DWH_IAM_ROLE_NAME       = config.get('DWH', 'DWH_IAM_ROLE_NAME')

DWH_SECURITY_GROUP      = config.get('DWH', 'DWH_SECURITY_GROUP')

(DWH_DB_USER, DWH_DB_PASSWORD, DWH_DB)

pd.DataFrame({'Param':
                    ['DWH_CLUSTER_TYPE', 'DWH_NUM_NODES', 'DWH_NODE_TYPE', 'DWH_CLUSTER_IDENTIFIER', 'DWH_DB', 'DWH_DB_USER', 'DWH_DB_PASSWORD', 'DWH_PORT', 'DWH_IAM_ROLE_NAME'],
              'Value':
                    [DWH_CLUSTER_TYPE, DWH_NUM_NODES, DWH_NODE_TYPE, DWH_CLUSTER_IDENTIFIER, DWH_DB, DWH_DB_USER, DWH_DB_PASSWORD, DWH_PORT, DWH_IAM_ROLE_NAME]
            })

ec2 = boto3.resource('ec2',
                       region_name="eu-central-1",
                       aws_access_key_id=KEY,
                       aws_secret_access_key=SECRET
                    )

s3 = boto3.resource('s3',
                       region_name="eu-central-1",
                       aws_access_key_id=KEY,
                       aws_secret_access_key=SECRET
                   )

iam = boto3.client('iam',
                     aws_access_key_id=KEY,
                     aws_secret_access_key=SECRET,
                     region_name='eu-central-1'
                  )

redshift = boto3.client('redshift',
                       region_name="eu-central-1",
                       aws_access_key_id=KEY,
                       aws_secret_access_key=SECRET
                       )

sampleDbBucket =  s3.Bucket("mh-upload-bucket")
for obj in sampleDbBucket.objects.filter(Prefix="OWID"):
    print(obj)

### CREATE IAM ROLE ###

#1.1 Create the role,
try:
    print("1.1 Creating a new IAM Role")
    dwhRole = iam.create_role(
        Path='/',
        RoleName=DWH_IAM_ROLE_NAME,
        Description = "Allows Redshift clusters to call AWS services on your behalf.",
        AssumeRolePolicyDocument=json.dumps(
            {'Statement': [{'Action': 'sts:AssumeRole',
               'Effect': 'Allow',
               'Principal': {'Service': 'redshift.amazonaws.com'}}],
             'Version': '2012-10-17'})
    )

except Exception as e:
    print(e)

print("1.2 Attaching Policy")

try:
    iam.attach_role_policy(RoleName=DWH_IAM_ROLE_NAME,
                       PolicyArn="arn:aws:iam::aws:policy/AmazonS3FullAccess"
                      )['ResponseMetadata']['HTTPStatusCode']
except Exception as e:
    print(e)

print("1.3 Get the IAM role ARN")
roleArn = iam.get_role(RoleName=DWH_IAM_ROLE_NAME)['Role']['Arn']

print(roleArn)

### CREATE CLUSTER ###

try:
    response = redshift.create_cluster(
        #HW
        ClusterType=DWH_CLUSTER_TYPE,
        NodeType=DWH_NODE_TYPE,
        NumberOfNodes=int(DWH_NUM_NODES),

        #Identifiers & Credentials
        DBName=DWH_DB,
        ClusterIdentifier=DWH_CLUSTER_IDENTIFIER,
        MasterUsername=DWH_DB_USER,
        MasterUserPassword=DWH_DB_PASSWORD,

        #Roles (for s3 access)
        IamRoles=[roleArn],

        VpcSecurityGroupIds=[
            DWH_SECURITY_GROUP
    ]
    )
except Exception as e:
    print(e)

### CHECK CLUSTER STATUS ###

def prettyRedshiftProps(props):
    pd.set_option('display.max_colwidth', None)
    keysToShow = ["ClusterIdentifier", "NodeType", "ClusterStatus", "MasterUsername", "DBName", "Endpoint", "NumberOfNodes", 'VpcId']
    x = [(k, v) for k,v in props.items() if k in keysToShow]
    return pd.DataFrame(data=x, columns=["Key", "Value"])

myClusterProps = redshift.describe_clusters(ClusterIdentifier=DWH_CLUSTER_IDENTIFIER)['Clusters'][0]
prettyRedshiftProps(myClusterProps)

### PRINT ENDPOINT AND ARN ###
### DO NOT RUN UNTIL CLUSTER IS AVAILABLE! ###

#if redshift.describe_clusters(ClusterIdentifier=DWH_CLUSTER_IDENTIFIER)['Clusters'][0]['ClusterStatus'] == 'available':
#    DWH_ENDPOINT = myClusterProps['Endpoint']['Address']
#    DWH_ROLE_ARN = myClusterProps['IamRoles'][0]['IamRoleArn']
#    print("DWH_ENDPOINT :: ", DWH_ENDPOINT)
#    print("DWH_ROLE_ARN :: ", roleArn)

### TEST CONNECTION USING SQL ###

#conn_string="postgresql://{}:{}@{}:{}/{}".format(DWH_DB_USER, DWH_DB_PASSWORD, DWH_ENDPOINT, DWH_PORT,DWH_DB)
#print(conn_string)
#%sql $conn_string

### DELETE CLUSTER ###

#redshift.delete_cluster( ClusterIdentifier=DWH_CLUSTER_IDENTIFIER,  SkipFinalClusterSnapshot=True)
