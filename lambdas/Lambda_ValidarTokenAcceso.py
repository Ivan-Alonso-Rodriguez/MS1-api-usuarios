import boto3
from datetime import datetime
import json
import os  # para leer variables de entorno

def lambda_handler(event, context):
    try:
        print("Evento recibido:", event)

        # Asegurarse que el cuerpo sea JSON
        body = json.loads(event['body'])
        token = body.get('token')

        if not token:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Token no proporcionado'})
            }

        # Consultar DynamoDB
        dynamodb = boto3.resource('dynamodb')
        tokens_table_name = os.environ['TOKENS_TABLE']
        table = dynamodb.Table(tokens_table_name)
        response = table.get_item(Key={'token': token})

        print("Respuesta de DynamoDB:", response)

        if 'Item' not in response:
            return {
                'statusCode': 403,
                'body': json.dumps({'error': 'Token no existe'})
            }

        expires = response['Item']['expires']
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if now > expires:
            return {
                'statusCode': 403,
                'body': json.dumps({'error': 'Token expirado'})
            }

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Token válido'})
        }

    except Exception as e:
        print("ERROR:", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
