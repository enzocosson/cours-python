import json
from requests import HTTPError
from http import HTTPStatus
from functools import wraps
import os
import boto3

def exception_handler(func):
    @wraps(func)
    def wrapper(event, context):
        print(event)
        response = {}
        try:
            token = event['headers'].get('x-api-key')
            if not token:
                raise PermissionError('Token is missing')
            res = func(event, context, token)
            if res:
                response['body'] = json.dumps(res)
            response['statusCode'] = HTTPStatus.OK
        except HTTPError as error:
            response['statusCode'] = error.response.status_code
            response['body'] = str(error)
        except PermissionError as error:
            response['statusCode'] = HTTPStatus.FORBIDDEN
            response['body'] = str(error)
        except Exception as error:
            response['statusCode'] = HTTPStatus.INTERNAL_SERVER_ERROR
            response['body'] = str(error)
        return response
    return wrapper


@exception_handler
def handler(event, context, token):
    user_table_name = os.environ.get('STORAGE_USERS_NAME')
    dynamodb = boto3.resource('dynamodb', region_name="eu-west-1")
    table = dynamodb.Table(user_table_name)
    
    res = table.scan(FilterExpression=boto3.dynamodb.conditions.Attr('token').eq(token))
    data = res.get('Items')
    
    if not data:
        return "User Missing"
    
    return data[0]['email']
