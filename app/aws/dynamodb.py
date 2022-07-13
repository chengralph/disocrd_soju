"""
DynamoDB Service methods
"""

from app.aws.common import get_boto_resource
from app.common.log import get_logger
import typing
log = get_logger("standard")


def get_item(item: dict, table: str, region: str = "us-east-1"):
    """
    Get Item from DynamoDB
    @param item:
    @param table:
    @param region:
    @return:
    """
    log.info('Getting Items from DynamoDB Table')
    dynamodb = get_boto_resource(
        resource='dynamodb',
        region=region)
    dynamodb_table = dynamodb.Table(table)
    response = dynamodb_table.get_item(
        Key=item
    )
    log.info(f"Get Item Response: {response}")
    return response.get("Item", False)


def get_items(table: str, region: str = "us-east-1"):
    """
    Get Item from DynamoDB
    @param table:
    @param region:
    @return:
    """
    log.info('Getting Items from DynamoDB Table')
    dynamodb = get_boto_resource(
        resource='dynamodb',
        region=region)
    dynamodb_table = dynamodb.Table(table)
    response = dynamodb_table.scan()
    data = response['Items']
    while 'LastEvaluatedKey' in response:
        response = dynamodb_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response['Items'])
    return data


def put_item(table: str, item: dict, region: str = "us-east-1"):
    """
    Put Item to DynamoDB
    @param table:
    @param item:
    @param region:
    @return:
    """
    log.info(f'Putting Item to DynamoDB Table: {item}')
    dynamodb = get_boto_resource(
        resource='dynamodb',
        region=region)
    dynamodb_table = dynamodb.Table(table)
    return dynamodb_table.put_item(
        Item=item
    )


def update_item(item: dict, key: str, value: typing.Any, table: str, region: str = "us-east-1"):
    """
    Update Item to DynamoDB
    @param key:
    @param value:
    @param table:
    @param item:
    @param region:
    @return:
    """
    log.info('Putting Items to DynamoDB Table')
    dynamodb = get_boto_resource(
        resource='dynamodb',
        region=region)
    dynamodb_table = dynamodb.Table(table)
    return dynamodb_table.update_item(
        Key=item,
        UpdateExpression="SET #tkn =:val",
        ExpressionAttributeValues={
            ':val': value},
        ExpressionAttributeNames={
            '#tkn': key},
        ReturnValues="UPDATED_NEW")
