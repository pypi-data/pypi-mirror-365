import boto3, json
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, NoRegionError, WaiterError
from .utils import generate_ulid

# import time
# import os
# import base64

# def generate_ulid():
#     # Get the current timestamp in milliseconds
#     timestamp = int(time.time() * 1000)
#     # Generate 10 bytes of random data
#     random_data = os.urandom(10)
#     # Encode the timestamp and random data using Crockford's Base32 encoding
#     ulid = base64.b32encode(timestamp.to_bytes(6, 'big') + random_data).decode('utf-8').replace('=', '')
#     return ulid

class Database:
    def __init__(self, region_name='ap-south-1'):  # Hardcoded region name for Mumbai, India
        AWS_ACCESS_KEY_ID = 'AKIARQUMPKD3FKM7KH7Y'
        AWS_SECRET_ACCESS_KEY = 'RC7iw5SIQFsMut43lOTApwPTO3bGSTY2Lj4oDE1X'
        AWS_REGION = 'ap-south-1'  # e.g., 'us-west-2'

        # Create a session using your credentials
        try:
            session = boto3.Session(
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                region_name=AWS_REGION
            )
            print(f"Session created with region: {session.region_name}")
        except NoRegionError:
            print("No region specified or region not recognized.")
        except Exception as e:
            print(f"Error creating session: {e}")

        # Create a DynamoDB client
        try:
            self.dynamodb = session.resource('dynamodb', region_name=AWS_REGION)
            print(f"DynamoDB resource created with region: {AWS_REGION}")
        except NoRegionError:
            print("No region specified or region not recognized.")
        except Exception as e:
            print(f"Error creating DynamoDB resource: {e}")

class CloudBase:
    def __init__(self, table_name):
        self.db = Database()
        self.table_name = table_name
        self.table = self.db.dynamodb.Table(table_name)
        print("table initiated.")
        self.create_table_if_not_exists()

    def create_table_if_not_exists(self):
        try:
            self.db.dynamodb.meta.client.describe_table(TableName=self.table_name)
            print(f"Table {self.table_name} already exists.")
        except self.db.dynamodb.meta.client.exceptions.ResourceNotFoundException:
            print(f"Table {self.table_name} does not exist. Creating it now.")
            self.db.dynamodb.create_table(
                TableName=self.table_name,
                KeySchema=[
                    {
                        'AttributeName': 'id',
                        'KeyType': 'HASH'  # Partition key
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'id',
                        'AttributeType': 'S'
                    }
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            )
            # Wait for the table to be created
            self.db.dynamodb.meta.client.get_waiter('table_exists').wait(TableName=self.table_name)
            print(f"Table {self.table_name} created successfully.")

    # def fetchall(self, query=None):
    #     scan_kwargs = {}
    #     if query:
    #         filter_expression = self._build_filter_expression(query)
    #         scan_kwargs['FilterExpression'] = filter_expression

    #     response = self.table.scan(**scan_kwargs)
    #     return response.get('Items', [])

    def fetchall(self, query=None):
        scan_kwargs = {}
        if query:
            filter_expression, expression_attribute_names, expression_attribute_values = self._build_filter_expression(query)
            scan_kwargs['FilterExpression'] = filter_expression
            scan_kwargs['ExpressionAttributeNames'] = expression_attribute_names
            scan_kwargs['ExpressionAttributeValues'] = expression_attribute_values

        response = self.table.scan(**scan_kwargs)
        return response.get('Items', [])


    def fetch(self, query=None):
        return self.fetchall(query)

    def put(self, data):
        id = str(generate_ulid())
        data['id'] = id
        self.table.put_item(Item=data)
        return {"id": id, "msg": "success"}

    def update(self, query, id):
        update_expression = self._build_update_expression(query)
        self.table.update_item(
            Key={'id': id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues={f":{k}": v for k, v in query.items()}
        )

    def delete(self, id):
        self.table.delete_item(Key={'id': id})

    def truncate(self):
        scan_kwargs = {}
        while True:
            response = self.table.scan(**scan_kwargs)
            items = response.get('Items', [])
            if not items:
                break
            with self.table.batch_writer() as batch:
                for item in items:
                    batch.delete_item(Key={'id': item['id']})
            if 'LastEvaluatedKey' not in response:
                break
            scan_kwargs['ExclusiveStartKey'] = response['LastEvaluatedKey']

    def drop(self):
        self.table.delete()

    # def _build_filter_expression(self, query):
    #     expressions = []
    #     for key, value in query.items():
    #         if "?contains" in key:
    #             field = key.split("?")[0]
    #             expressions.append(f"contains({field}, :{field})")
    #         else:
    #             expressions.append(f"{key} = :{key}")
    #     return " AND ".join(expressions)

    def _build_filter_expression(self, query):
        expressions = []
        expression_attribute_names = {}
        expression_attribute_values = {}

        for key, value in query.items():
            if "?contains" in key:
                field = key.split("?")[0]
                attr_name = f"#{field}"
                attr_value = f":{field}"
                expressions.append(f"contains({attr_name}, {attr_value})")
                expression_attribute_names[attr_name] = field
                expression_attribute_values[attr_value] = value
            else:
                attr_name = f"#{key}"
                attr_value = f":{key}"
                expressions.append(f"{attr_name} = {attr_value}")
                expression_attribute_names[attr_name] = key
                expression_attribute_values[attr_value] = value

        filter_expression = " AND ".join(expressions)
        return filter_expression, expression_attribute_names, expression_attribute_values


    def _build_update_expression(self, query):
        expressions = []
        for key in query.keys():
            expressions.append(f"{key} = :{key}")
        return "SET " + ", ".join(expressions)

# db = CloudBase('my_another_table')

# # Insert data
# data = {
#     'name': 'Poonam',
#     'age': 30,
#     'email': 'john.doe@example.com'
# }

# print(db.put(data))  # {'id': 'generated_ulid', 'msg': 'success'}

# print(db.fetch())

# print(db.fetchall())
# # Fetch all records
# # all_records = db.fetchall()
# # print(all_records)

# # Fetch records with a specific query
# print(db.fetch({'name?contains': 'Man'}))