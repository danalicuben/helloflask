import os
import boto


AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY', '')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY', '')

_dynamodb_conn = boto.connect_dynamodb(AWS_ACCESS_KEY, AWS_SECRET_KEY)
DYNAMODB_TABLE_HELLOFLASK = _dynamodb_conn.get_table('HelloFlask')
