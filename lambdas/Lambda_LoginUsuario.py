import boto3
import hashlib
import uuid
from datetime import datetime, timedelta
import json

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def lambda_handler(event, context):
    try:
        print("Evento recibido:", event)

        # Convertir body JSON
        body = json.loads(event['body'])
        user_id = body.get('user_id')
        password = body.get('password')
        print("Usuario:", user_id)

        if not user_id or not password:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Faltan user_id o password'})
            }

        hashed_password = hash_password(password)

        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('t_usuarios')
        response = table.get_item(Key={ 'user_id': user_id })
        print("Respuesta DynamoDB:", response)

        if 'Item' not in response:
            return {
                'statusCode': 403,
                'body': json.dumps({'error': 'Usuario no existe'})
            }

        hashed_password_bd = response['Item']['password']
        if hashed_password != hashed_password_bd:
            return {
                'statusCode': 403,
                'body': json.dumps({'error': 'Password incorrecto'})
            }

        token = str(uuid.uuid4())
        fecha_hora_exp = datetime.now() + timedelta(minutes=60)

        table_tokens = dynamodb.Table('t_tokens_acceso')
        table_tokens.put_item(Item={
            'token': token,
            'expires': fecha_hora_exp.strftime('%Y-%m-%d %H:%M:%S')
        })

        return {
            'statusCode': 200,
            'body': json.dumps({'token': token})
        }

    except Exception as e:
        print("ERROR:", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
