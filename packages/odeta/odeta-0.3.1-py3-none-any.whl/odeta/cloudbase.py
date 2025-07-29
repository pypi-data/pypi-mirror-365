from pymongo import MongoClient
from pymongo.errors import ConfigurationError
import json
from contextlib import contextmanager
import time
import os
import base64
from datetime import datetime

def generate_ulid():
    timestamp = int(time.time() * 1000)
    random_data = os.urandom(10)
    ulid = base64.b32encode(timestamp.to_bytes(6, 'big') + random_data).decode('utf-8').replace('=', '')
    return ulid

class Database:
    def __init__(self, connection_string, db_name=None):
        self.client = MongoClient(connection_string)
        if db_name:
            self.db = self.client[db_name]
        else:
            try:
                self.db = self.client.get_database()
            except ConfigurationError:
                raise ValueError("No database specified in the connection string. Please provide a db_name.")

    @contextmanager
    def get_collection(self, collection_name):
        try:
            yield self.db[collection_name]
        finally:
            pass

class CloudBase:
    def __init__(self, connection_string, db_name="test"):
        self.db = Database(connection_string, db_name)

    def __call__(self, collection_name):
        return Collection(self.db, collection_name)

class Collection:
    def __init__(self, db, collection_name):
        self.db = db
        self.collection_name = collection_name

    def fetchall(self, query=None):
        with self.db.get_collection(self.collection_name) as collection:
            if query is None:
                results = collection.find()
            else:
                results = collection.find(self._transform_query(query))
            return [self._transform_document(doc) for doc in results]

    def fetch(self, query=None):
        return self.fetchall(query)
    
    def count(self, query=None):
        with self.db.get_collection(self.collection_name) as collection:
            if query:
                query = self._transform_query(query)
            else:
                query = {}
            return collection.count_documents(query)

    def get(self, _id):
        with self.db.get_collection(self.collection_name) as collection:
            result = collection.find_one({"_id": _id})
            return self._transform_document(result) if result else None

    def put(self, data):
        _id = str(generate_ulid())
        with self.db.get_collection(self.collection_name) as collection:
            data["_id"] = _id
            collection.insert_one(data)
        return {"_id": _id, "msg": "success"}

    def update(self, _id, data, partial=False):
        with self.db.get_collection(self.collection_name) as collection:
            if partial:
                result = collection.update_one({"_id": _id}, {"$set": data})
                if result.matched_count == 0:
                    nested_data = self._build_nested_document(data)
                    nested_data["_id"] = _id
                    collection.insert_one(nested_data)
            else:
                result = collection.replace_one({"_id": _id}, data, upsert=True)
            return {"_id": _id, "msg": "success"}

    def partial(self, _id, data):
        """Convenience method for partial updates, supports nested fields via dot notation."""
        return self.update(_id, data, partial=True)

    def nested_update(self, _id, updates, upsert=True):
        """Update nested fields in a document identified by _id."""
        with self.db.get_collection(self.collection_name) as collection:
            result = collection.update_one({"_id": _id}, {"$set": updates}, upsert=upsert)
            return {
                "_id": _id,
                "msg": "success",
                "matched_count": result.matched_count,
                "modified_count": result.modified_count,
                "upserted": result.upserted_id is not None
            }

    def delete(self, _id):
        with self.db.get_collection(self.collection_name) as collection:
            collection.delete_one({"_id": _id})
        return {"_id": _id, "msg": "success"}

    def truncate(self):
        with self.db.get_collection(self.collection_name) as collection:
            collection.delete_many({})
        return {"msg": "collection truncated"}

    def drop(self):
        with self.db.get_collection(self.collection_name) as collection:
            collection.drop()
        return {"msg": "collection dropped"}

    def _transform_query(self, query):
        transformed = {}
        for key, value in query.items():
            if "?contains" in key:
                field = key.split("?")[0]
                transformed[field] = {"$regex": value, "$options": "i"}
            else:
                transformed[key] = value
        return transformed

    def _transform_document(self, doc):
        if doc is None:
            return None
        doc['_id'] = doc.pop('_id')
        return doc

    def _build_nested_document(self, flat_data):
        """Convert a flat dictionary with dot notation into a nested structure."""
        nested = {}
        for key, value in flat_data.items():
            current = nested
            parts = key.split('.')
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = value
        return nested

# Example Usage
if __name__ == "__main__":
    pass

    # connection_string = "mongodb://localhost:27017/"
    # db = CloudBase(connection_string, db_name="test_db")
    # users = db("users")

    # # Insert a user
    # user_data = {"names": {"father": "x", "mother": "y"}}
    # result = users.put(user_data)
    # user_id = result["_id"]

    # # Partial update (flat)
    # users.partial(user_id, {"last_active_on": str(datetime.now())})

    # # Nested update
    # users.nested_update(user_id, {"names.father": "abc"})

    # # Fetch and print
    # updated_user = users.get(user_id)
    # print(updated_user)
    # pass

# from pymongo import MongoClient
# from pymongo.errors import ConfigurationError
# from bson.objectid import ObjectId
# import json
# from contextlib import contextmanager

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

# class Database:
#     # def __init__(self, connection_string):
#     #     self.client = MongoClient(connection_string)
#     #     self.db = self.client.get_database()

#     def __init__(self, connection_string, db_name):
#         self.client = MongoClient(connection_string)
#         if db_name:
#             self.db = self.client[db_name]
#         else:
#             try:
#                 self.db = self.client.get_database()
#             except ConfigurationError:
#                 raise ValueError("No database specified in the connection string. Please provide a db_name.")


#     @contextmanager
#     def get_collection(self, collection_name):
#         try:
#             yield self.db[collection_name]
#         finally:
#             pass

# class CloudBase:
#     def __init__(self, connection_string, db_name="test"):
#         self.db = Database(connection_string, db_name)

#     def __call__(self, collection_name):
#         return Collection(self.db, collection_name)

# class Collection:
#     def __init__(self, db, collection_name):
#         self.db = db
#         self.collection_name = collection_name

#     def fetchall(self, query=None):
#         with self.db.get_collection(self.collection_name) as collection:
#             if query is None:
#                 results = collection.find()
#             else:
#                 results = collection.find(self._transform_query(query))
#             return [self._transform_document(doc) for doc in results]

#     def fetch(self, query=None):
#         return self.fetchall(query)

#     def get(self, id):
#         with self.db.get_collection(self.collection_name) as collection:
#             result = collection.find_one({"_id": id})
#             return self._transform_document(result) if result else None

#     def put(self, data):
#         id = str(generate_ulid())
#         with self.db.get_collection(self.collection_name) as collection:
#             data["_id"] = id
#             collection.insert_one(data)
#         return {"id": id, "msg": "success"}

#     def update(self, query, id):
#         with self.db.get_collection(self.collection_name) as collection:
#             result = collection.update_one({"_id": id}, {"$set": query})
#             if result.matched_count == 0:
#                 collection.insert_one({"_id": id, **query})

#     def delete(self, id):
#         with self.db.get_collection(self.collection_name) as collection:
#             collection.delete_one({"_id": id})

#     def truncate(self):
#         with self.db.get_collection(self.collection_name) as collection:
#             collection.delete_many({})

#     def drop(self):
#         with self.db.get_collection(self.collection_name) as collection:
#             collection.drop()

#     def _transform_query(self, query):
#         transformed = {}
#         for key, value in query.items():
#             if "?contains" in key:
#                 field = key.split("?")[0]
#                 transformed[field] = {"$regex": value, "$options": "i"}
#             else:
#                 transformed[key] = value
#         return transformed

#     def _transform_document(self, doc):
#         if doc is None:
#             return None
#         doc['id'] = doc.pop('_id')
#         return doc
    
# # # -- MongoDB Below 

# # from pymongo import MongoClient
# # from pymongo.errors import ConfigurationError
# # from bson.objectid import ObjectId
# # import json
# # from contextlib import contextmanager
# # from .utils import generate_ulid

# # class Database:
# #     # def __init__(self, connection_string):
# #     #     self.client = MongoClient(connection_string)
# #     #     self.db = self.client.get_database()

# #     def __init__(self, connection_string, db_name="test"):
# #         self.client = MongoClient(connection_string)
# #         if db_name:
# #             self.db = self.client[db_name]
# #         else:
# #             try:
# #                 self.db = self.client.get_database()
# #             except ConfigurationError:
# #                 raise ValueError("No database specified in the connection string. Please provide a db_name.")


# #     @contextmanager
# #     def get_collection(self, collection_name):
# #         try:
# #             yield self.db[collection_name]
# #         finally:
# #             pass

# # class CloudBase:
# #     def __init__(self, connection_string, db_name="test"):
# #         self.db = Database(connection_string, db_name="test")

# #     def __call__(self, collection_name):
# #         return Collection(self.db, collection_name)

# # class Collection:
# #     def __init__(self, db, collection_name):
# #         self.db = db
# #         self.collection_name = collection_name

# #     def fetchall(self, query=None):
# #         with self.db.get_collection(self.collection_name) as collection:
# #             if query is None:
# #                 results = collection.find()
# #             else:
# #                 results = collection.find(self._transform_query(query))
# #             return [self._transform_document(doc) for doc in results]

# #     def fetch(self, query=None):
# #         return self.fetchall(query)

# #     def get(self, id):
# #         with self.db.get_collection(self.collection_name) as collection:
# #             result = collection.find_one({"_id": id})
# #             return self._transform_document(result) if result else None

# #     def put(self, data):
# #         id = str(generate_ulid())
# #         with self.db.get_collection(self.collection_name) as collection:
# #             data["_id"] = id
# #             collection.insert_one(data)
# #         return {"id": id, "msg": "success"}

# #     def update(self, query, id):
# #         with self.db.get_collection(self.collection_name) as collection:
# #             result = collection.update_one({"_id": id}, {"$set": query})
# #             if result.matched_count == 0:
# #                 collection.insert_one({"_id": id, **query})

# #     def delete(self, id):
# #         with self.db.get_collection(self.collection_name) as collection:
# #             collection.delete_one({"_id": id})

# #     def truncate(self):
# #         with self.db.get_collection(self.collection_name) as collection:
# #             collection.delete_many({})

# #     def drop(self):
# #         with self.db.get_collection(self.collection_name) as collection:
# #             collection.drop()

# #     def _transform_query(self, query):
# #         transformed = {}
# #         for key, value in query.items():
# #             if "?contains" in key:
# #                 field = key.split("?")[0]
# #                 transformed[field] = {"$regex": value, "$options": "i"}
# #             else:
# #                 transformed[key] = value
# #         return transformed

# #     def _transform_document(self, doc):
# #         if doc is None:
# #             return None
# #         doc['id'] = doc.pop('_id')
# #         return doc


# # # -- Postgres Below 

# # # from sqlalchemy import create_engine, Column, String, JSON, Table as SQLATable, MetaData
# # # from sqlalchemy.orm import sessionmaker, declarative_base
# # # from sqlalchemy.exc import SQLAlchemyError
# # # from sqlalchemy import inspect
# # # import json
# # # from contextlib import contextmanager
# # # from .utils import generate_ulid

# # # Base = declarative_base()
# # # # this is latest

# # # class Database:
# # #     def __init__(self, db_url):
# # #         self.engine = create_engine(db_url)
# # #         self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
# # #         self.metadata = MetaData()

# # #     @contextmanager
# # #     def get_session(self):
# # #         session = self.SessionLocal()
# # #         try:
# # #             yield session
# # #         finally:
# # #             session.close()

# # # class CloudBase:
# # #     def __init__(self, db_url):
# # #         self.db = Database(db_url)

# # #     def __call__(self, table_name):
# # #         return Table(self.db, table_name)

# # # class Table:
# # #     def __init__(self, db, table_name):
# # #         self.db = db
# # #         self.table_name = table_name
# # #         self.table = self.get_or_create_table()

# # #     def get_or_create_table(self):
# # #         inspector = inspect(self.db.engine)
# # #         if not inspector.has_table(self.table_name):
# # #             table = SQLATable(self.table_name, self.db.metadata,
# # #                 Column('id', String, primary_key=True),
# # #                 Column('data', JSON)
# # #             )
# # #             self.db.metadata.create_all(self.db.engine)
# # #         else:
# # #             table = SQLATable(self.table_name, self.db.metadata, autoload_with=self.db.engine)
# # #         return table

# # #     def parse_result(self, row):
# # #         try:
# # #             data = json.loads(row.data) if isinstance(row.data, str) else row.data
# # #             return {'id': row.id, **data}
# # #         except json.JSONDecodeError:
# # #             print(f"Warning: Could not parse JSON for id {row.id}. Returning raw data.")
# # #             return {'id': row.id, 'data': row.data}

# # #     def fetchall(self, query=None):
# # #         with self.db.get_session() as session:
# # #             results = session.query(self.table).all()
# # #             parsed_results = [self.parse_result(row) for row in results]
# # #             if query is None:
# # #                 return parsed_results
# # #             else:
# # #                 return self.filter_results(parsed_results, query)

# # #     def fetch(self, query=None):
# # #         return self.fetchall(query)

# # #     def filter_results(self, results, query):
# # #         filtered_results = []
# # #         for result in results:
# # #             match = True
# # #             for key, value in query.items():
# # #                 if "?contains" in key:
# # #                     field = key.split("?")[0]
# # #                     if value.lower() not in str(result.get(field, "")).lower():
# # #                         match = False
# # #                         break
# # #                 else:
# # #                     if result.get(key) != value:
# # #                         match = False
# # #                         break
# # #             if match:
# # #                 filtered_results.append(result)
# # #         return filtered_results

# # #     def put(self, data):
# # #         id = str(generate_ulid())
# # #         with self.db.get_session() as session:
# # #             new_row = self.table.insert().values(id=id, data=data)
# # #             session.execute(new_row)
# # #             session.commit()
# # #         return {"id": id, "msg": "success"}

# # #     def update(self, query, id):
# # #         with self.db.get_session() as session:
# # #             update_stmt = self.table.update().where(self.table.c.id == id).values(data=query)
# # #             session.execute(update_stmt)
# # #             session.commit()

# # #     def delete(self, id):
# # #         with self.db.get_session() as session:
# # #             delete_stmt = self.table.delete().where(self.table.c.id == id)
# # #             session.execute(delete_stmt)
# # #             session.commit()

# # #     def truncate(self):
# # #         with self.db.get_session() as session:
# # #             session.execute(self.table.delete())
# # #             session.commit()

# # #     def drop(self):
# # #         self.table.drop(self.db.engine)

# # #     def get(self, id):
# # #         with self.db.get_session() as session:
# # #             result = session.query(self.table).filter(self.table.c.id == id).first()
# # #             return self.parse_result(result) if result else None
        
# # # # --------------------------------------------------------------------------------------------------------------------------------
# # #  #   #  # # #  Initialize the database connection (example with SQLite)
# # # import os
# # # os.system("clear")

# # # db_url = "urllll"
# # # db = CloudBase(db_url)

# # # # # Access the 'users' table
# # # users = db('users')

# # # # # Example: Insert a user
# # # # new_user = users.put({"name": "John Smith", "email": "john@example.com"})
# # # # print("Inserted user:", new_user)

# # # # # Get the user by id
# # # # user_id = new_user['id']
# # # # retrieved_user = users.get(user_id)
# # # # print("Retrieved user:", retrieved_user)

# # # # Fetch all users
# # # all_users = users.fetch()
# # # print("All users:", all_users)

# # # print("Filtered users:", all_users.fetch({ "name?contains" : "John"}))

# # # # # Update a user
# # # # users.update({"name": "John Smith", "email": "john.updated@example.com"}, user_id)
# # # # updated_user = users.get(user_id)
# # # # print("Updated user:", updated_user)

# # # # # Delete a user
# # # # users.delete(user_id)
# # # # deleted_user = users.get(user_id)
# # # # print("Deleted user (should be None):", deleted_user)