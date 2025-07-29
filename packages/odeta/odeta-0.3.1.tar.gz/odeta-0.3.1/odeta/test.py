# # from odeta import cloudbase
# from cloudbase import CloudBase as cloudbase

# # Initialize the database with the table name directly
# db = cloudbase('my_table')

# # Insert data
# data = {
#     'name': 'John Doe',
#     'age': 30,
#     'email': 'john.doe@example.com'
# }
# response = db.put(data)
# print(response)  # {'id': 'generated_ulid', 'msg': 'success'}

# # Fetch all records
# all_records = db.fetchall()
# print(all_records)

# # Fetch records with a specific query
# filtered_records = db.fetch({'name?contains': 'John'})
# print(filtered_records)

# # # Update a record by its ID
# # update_data = {
# #     'name': 'Jane Doe',
# #     'age': 25,
# #     'email': 'jane.doe@example.com'
# # }
# # db.update(update_data, 'record_id')

# # # Delete a record by its ID
# # db.delete('record_id')

# # # Truncate the table
# # db.truncate()

# # # Drop the table
# # db.drop()




# import boto3
# from botocore.exceptions import NoCredentialsError, PartialCredentialsError, NoRegionError, WaiterError

# # Replace these with your own credentials
# AWS_ACCESS_KEY_ID = 'AKIARQUMPKD3FKM7KH7Y'
# AWS_SECRET_ACCESS_KEY = 'RC7iw5SIQFsMut43lOTApwPTO3bGSTY2Lj4oDE1X'
# AWS_REGION = 'ap-south-1'  # e.g., 'us-west-2'

# # Create a session using your credentials
# try:
#     session = boto3.Session(
#         aws_access_key_id=AWS_ACCESS_KEY_ID,
#         aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
#         region_name=AWS_REGION
#     )
#     print(f"Session created with region: {session.region_name}")
# except NoRegionError:
#     print("No region specified or region not recognized.")
# except Exception as e:
#     print(f"Error creating session: {e}")

# # Create a DynamoDB client
# try:
#     dynamodb = session.resource('dynamodb', region_name=AWS_REGION)
#     print(f"DynamoDB resource created with region: {AWS_REGION}")
# except NoRegionError:
#     print("No region specified or region not recognized.")
# except Exception as e:
#     print(f"Error creating DynamoDB resource: {e}")

# # Create a table
# def create_table():
#     try:
#         table = dynamodb.create_table(
#             TableName='TestTable',
#             KeySchema=[
#                 {
#                     'AttributeName': 'id',
#                     'KeyType': 'HASH'  # Partition key
#                 }
#             ],
#             AttributeDefinitions=[
#                 {
#                     'AttributeName': 'id',
#                     'AttributeType': 'N'
#                 }
#             ],
#             ProvisionedThroughput={
#                 'ReadCapacityUnits': 5,
#                 'WriteCapacityUnits': 5
#             }
#         )
#         print("Table status:", table.table_status)

#         # Wait for the table to be created
#         table.meta.client.get_waiter('table_exists').wait(TableName='TestTable')
#         print("Table created successfully.")

#     except Exception as e:
#         print(f"Error creating table: {e}")

# # Insert an item into the table
# def insert_item():
#     try:
#         table = dynamodb.Table('TestTable')
#         response = table.put_item(
#             Item={
#                 'id': 1,
#                 'name': 'Test Item',
#                 'description': 'This is a test item'
#             }
#         )
#         print("PutItem succeeded:", response)
#     except Exception as e:
#         print(f"Error inserting item: {e}")

# # Get an item from the table
# def get_item():
#     try:
#         table = dynamodb.Table('TestTable')
#         response = table.get_item(
#             Key={
#                 'id': 1
#             }
#         )
#         item = response.get('Item')
#         print("GetItem succeeded:", item)
#     except Exception as e:
#         print(f"Error getting item: {e}")

# # Delete the table
# def delete_table():
#     try:
#         table = dynamodb.Table('TestTable')
#         table.delete()
#         print("Table deletion initiated")
#     except Exception as e:
#         print(f"Error deleting table: {e}")

# if __name__ == "__main__":
#     try:
#         create_table()
#         insert_item()
#         get_item()
#         # delete_table()
#     except NoCredentialsError:
#         print("Credentials not available")
#     except PartialCredentialsError:
#         print("Incomplete credentials provided")
#     except NoRegionError:
#         print("No region specified or region not recognized.")
#     except Exception as e:
#         print(f"An error occurred: {e}")
