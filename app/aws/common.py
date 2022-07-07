"""Common AWS Methods"""
import boto3
import os
from app.common.log import get_logger

log = get_logger()


def get_boto_resource(resource: str, region: str):
    """
    Get Boto3 Resource
    @param resource:
    @param region:
    @return:
    """
    log.info("Get Boto3 Client")
    try:
        credentials = get_credentials()
        aws_resource = boto3.resource(
            service_name=resource,
            region_name=region,
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken'],
        )
        log.info("Boto client created")
        return aws_resource
    except TypeError as type_error:
        log.error(type_error)
        raise type_error


def get_credentials():
    """
    Get Credentials
    @return:
    """
    log.info("Get Credentials")
    sts_client = boto3.client('sts')
    assumed_role_object = sts_client.assume_role(
        RoleArn=os.getenv("AWS_ASSUME_ROLE"),
        RoleSessionName="Discord_Soju_Session"
    )
    credentials = assumed_role_object['Credentials']
    log.info("Credentials created for Discord Soju")
    return credentials
