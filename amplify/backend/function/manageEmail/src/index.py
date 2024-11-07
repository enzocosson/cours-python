import json
import os
import boto3
import uuid
import hmac
import hashlib
import time

def generate_hmac_token(payload):
    message = json.dumps(payload)
    timestamp = str(int(time.time()))
    message_with_timestamp = f"{message}{timestamp}".encode("utf-8")
    hmac_token = hmac.new(f"{payload['id']}{payload['email']}".encode("utf-8"), message_with_timestamp, hashlib.sha256).hexdigest()
    return hmac_token

def handler(event, context):
    try:
        user_table_name = os.environ.get('STORAGE_USERS_NAME')
        dynamodb = boto3.resource('dynamodb', region_name="eu-west-1")
        table = dynamodb.Table(user_table_name)
        
        body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        
        email = body.get('email')
        if not email:
            return {'statusCode': 400, 'body': 'Email is required'}
        
        res = table.query(
            IndexName='emails',
            KeyConditionExpression='email = :email',
            ExpressionAttributeValues={':email': email}
        )
        
        if not res['Items']:  
            user_id = str(uuid.uuid4())
            token = generate_hmac_token({'email': email, 'id': user_id})
            
            user_data = {
                'id': user_id,
                'email': email,
                'token': token
            }
            
            lambda_client = boto3.client('lambda')
            create_user_event = {
                'body': json.dumps(user_data)
            }
            print(json.dumps(create_user_event))  
            lambda_client.invoke(
                FunctionName=os.environ.get('FUNCTION_CREATEUSER_NAME'),
                InvocationType='Event',
                Payload=json.dumps(create_user_event)
            )
                
        
        else:  
            user_id = res['Items'][0].get('id')
            token = res['Items'][0].get('token')
            return {'statusCode': 200, 'body': json.dumps({'user_id': user_id, 'token': token})}
    
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return {'statusCode': 500, 'body': 'Internal server error'}
