import boto3
import hashlib
import json

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        user_id = body.get('user_id')
        password = body.get('password')
        name = body.get('name')

        if not user_id or not password:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'user_id y password son requeridos'})
            }

        hashed_password = hash_password(password)

        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('t_MS1_usuarios')

        item = {
            'user_id': user_id,
            'password': hashed_password
        }

        if name:
            item['name'] = name

        table.put_item(Item=item)

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Usuario registrado correctamente', 'user_id': user_id})
        }

    except Exception as e:
        print("ERROR:", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
