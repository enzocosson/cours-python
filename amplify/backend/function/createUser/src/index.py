import json
import os
import boto3

def create_user(event, context):
    try:
        body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        user_id = body.get('id')
        email = body.get('email')
        token = body.get('token')
        
        if not user_id or not email or not token:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Missing user data'})
            }
        
        dynamodb = boto3.resource('dynamodb', region_name="eu-west-1")
        user_table_name = os.environ.get('STORAGE_USERS_NAME')
        table = dynamodb.Table(user_table_name)
        
        table.put_item(Item={
            'id': user_id,
            'email': email,
            'token': token
        })
        
        return {
            'statusCode': 200,
            'body': json.dumps({'user_id': user_id, 'token': token})
        }
    
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return {'statusCode': 500, 'body': 'Internal server error'}
