import json
from requests import HTTPError
from http import HTTPStatus
from functools import wraps
import os
import boto3
import uuid
import hmac
import hashlib
import time

secret_key = "26506159-fa38-4a11-9b21-487297058631"

def exception_handler(func):
    @wraps(func)
    def wrapper(event, context):
        print(event)
        response = {}
        try:
            if event['headers'].get('x-api-key'):
                raise PermissionError('x-api-key missing or wrong')
            res = func(event, context)
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

def generate_hmac_token(payload):
    message = json.dumps(payload)
    timestamp = str(int(time.time()))
    message_with_timestamp = f"{message}{timestamp}".encode("utf-8")
    hmac_token = hmac.new(secret_key.encode("utf-8"), message_with_timestamp, hashlib.sha256).hexdigest()
    return hmac_token

@exception_handler
def handler(event, context):
    user_table_name = os.environ.get('STORAGE_USERS_NAME')
    dynamodb = boto3.resource('dynamodb', region_name="eu-west-1")
    table = dynamodb.Table(user_table_name)
    
    try:
        body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
    except json.JSONDecodeError:
        raise ValueError('Le corps de la requête n\'est pas au format JSON.')
    
    email = body.get('email')
    
    if not email:
        raise ValueError('Email is required')
    
    res = table.query(
        IndexName='emails',
        KeyConditionExpression='email = :email',
        ExpressionAttributeValues={':email': email}
    )
    
    if not res['Items']:  
        user_id = str(uuid.uuid4())
        token = generate_hmac_token({'email': email, 'id': user_id})
        table.put_item(Item={
            'id': user_id,
            'email': email,
            'token': token
        })
        return {'user_id': user_id, 'token': token}
    
    else:
        user_id = res['Items'][0].get('id')
        token = res['Items'][0].get('token')
        return {'user_id': user_id, 'token': token}
