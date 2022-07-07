"""
DynamoDB Service methods
"""
from app.common.log import get_logger
from app.aws.common import get_boto_resource

log = get_logger()


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
    dynamo_table = dynamodb.Table(table)
    response = dynamo_table.scan()
    data = response['Items']
    while 'LastEvaluatedKey' in response:
        response = dynamo_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
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
    log.info('Putting Items to DynamoDB Table')
    dynamodb = get_boto_resource(
        resource='dynamodb',
        region=region)
    return dynamodb.put_item(
        TableName=table,
        Item=item
    )


def update_item(table: str, item: dict, region: str = "us-east-1"):
    """
    Update Item to DynamoDB
    @param table:
    @param item:
    @param region:
    @return:
    """
    log.info('Putting Items to DynamoDB Table')
    dynamodb = get_boto_resource(
        resource='dynamodb',
        region=region)
    return dynamodb.update_item(
        TableName=table,
        Item=item
    )
