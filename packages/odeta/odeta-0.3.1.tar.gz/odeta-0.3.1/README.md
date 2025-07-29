# ODETA

ODETA is a lightweight ORM-like library for SQLite that allows you to perform NoSQL-like operations. It provides a simple and intuitive interface for interacting with SQLite databases, making it easy to store and retrieve JSON data.

## Features

- **CRUD Operations**: Easily perform create, read, update, and delete operations.
- **Querying**: Support for simple and complex queries.
- **ULID Generation**: Automatically generate ULIDs for unique record identifiers.
- **Table Management**: Create, drop, and truncate tables.
- **Row Counting**: Count the number of rows in a table.
- **Fetch by ID**: Retrieve a single row by its ID.

## Installation

You can install ODETA using pip:

```bash
pip install odeta
```

## Usage

### Initialization

First, import the `LocalBase` class and create a database instance:

```python
from odeta import LocalBase

db = LocalBase('my_database.db')
```

### Creating and Inserting Data

Create a table and insert data:

```python
table = db('my_table')

data = {
    'name': 'John Doe',
    'age': 30,
    'email': 'john.doe@example.com'
}

response = table.put(data)
print(response)  # {'id': 'system_generated_unqiue_id', 'msg': 'success'}
```

### Querying Data

Fetch all records or filter records based on a query:

```python
# Fetch all records
all_records = table.fetchall() # You can put query too in this fetchall({...}), it will gather all rows with OR condition.
print(all_records)

# Fetch records with a specific query AND condition.
filtered_records = table.fetch({'name?contains': 'John'})
print(filtered_records)
```

### Updating Data

Update a record by its ID:

```python
update_data = {
    'name': 'Jane Doe',
    'age': 25,
    'email': 'jane.doe@example.com'
}

table.update(update_data, 'record_id')
```

### Deleting Data

Delete a record by its ID:

```python
table.delete('record_id')
```

### Additional Operations

#### Truncate Table

Remove all rows from the table:

```python
table.truncate()
```

#### Drop Table

Completely remove the table from the database:

```python
table.drop()
```

#### Count Rows

Count the number of rows in the table:

```python
row_count = table.count()
print(row_count)
```

#### Find by ID

Retrieve a single row by its ID:

```python
record = table.get('record_id')
print(record)
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Contact

For any questions or feedback, please contact [tech.manujpr@gmail.com](mailto:tech.manujpr@gmail.com).

---

Thank you for using ODETA!