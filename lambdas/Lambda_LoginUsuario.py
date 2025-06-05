import boto3
import hashlib
import uuid
from datetime import datetime, timedelta
import json

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        user_id = body['user_id']
        password = body['password']
        hashed_password = hash_password(password)

        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('t_usuarios')
        response = table.get_item(Key={ 'user_id': user_id })

        if 'Item' not in response:
            return {
                'statusCode': 403,
                'body': json.dumps({'error': 'Usuario no existe'})
            }

        hashed_password_bd = response['Item']['password']
        if hashed_password == hashed_password_bd:
            token = str(uuid.uuid4())
            fecha_hora_exp = datetime.now() + timedelta(minutes=60)
            registro = {
                'token': token,
                'expires': fecha_hora_exp.strftime('%Y-%m-%d %H:%M:%S')
            }
            table_tokens = dynamodb.Table('t_tokens_acceso')
            table_tokens.put_item(Item=registro)
        else:
            return {
                'statusCode': 403,
                'body': json.dumps({'error': 'Password incorrecto'})
            }

        return {
            'statusCode': 200,
            'token': token
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
