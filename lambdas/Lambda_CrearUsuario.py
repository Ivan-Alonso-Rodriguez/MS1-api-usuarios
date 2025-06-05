import boto3
import hashlib
import json

# Hashear contraseña
def hash_password(password):
    # Retorna la contraseña hasheada
    return hashlib.sha256(password.encode()).hexdigest()

# Función que maneja el registro de user y validación del password

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        user_id = body.get('user_id')
        password = body.get('password')

        if user_id and password:
            hashed_password = hash_password(password)
            dynamodb = boto3.resource('dynamodb')
            t_usuarios = dynamodb.Table('t_usuarios')
            t_usuarios.put_item(
                Item={
                    'user_id': user_id,
                    'password': hashed_password
                }
            )
            mensaje = {
                'message': 'User registered successfully',
                'user_id': user_id
            }
            return {
                'statusCode': 200,
                'body': json.dumps(mensaje)
            }
        else:
            mensaje = {
                'error': 'Invalid request body: missing user_id or password'
            }
            return {
                'statusCode': 400,
                'body': json.dumps(mensaje)
            }

    except Exception as e:
        print("Exception:", str(e))
        mensaje = {
            'error': str(e)
        }
        return {
            'statusCode': 500,
            'body': json.dumps(mensaje)
        }
