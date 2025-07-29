
# SimpleORM

SimpleORM is a lightweight and easy-to-use Object-Relational Mapping (ORM) utility for Python built on top of SQLite. It provides basic CRUD (Create, Read, Update, Delete) operations by mapping Python classes directly to SQLite tables, simplifying database interactions without requiring complex setup.

## Features

- Automatically creates SQLite tables based on Python class annotations.
- Insert Python objects into the database.
- Retrieve all or single records as Python objects.
- Delete records by object instance or ID.
- Supports basic Python types: `int`, `str`, `float`.

## Installation

No external dependencies are required besides Python's built-in `sqlite3` module. Just include the `SimpleORM` class in your project.

## Usage

1. Define your data model as a Python class with type annotations.

```python
class User:
    id: int
    name: str
    age: int
```

2. Create a `SimpleORM` instance with the SQLite database filename:

```python
orm = SimpleORM("mydatabase.db")
```

3. Create the corresponding table for your model:

```python
orm.create_table(User)
```

4. Insert objects:

```python
user = User()
user.name = "Alice"
user.age = 25
orm.insert(user)
print(user.id)  # Auto-generated ID
```

5. Query all records:

```python
users = orm.get_all(User)
for u in users:
    print(u.id, u.name, u.age)
```

6. Query a single record by ID:

```python
user = orm.get_one(User, 1)
if user:
    print(user.name, user.age)
```

7. Delete records:

```python
orm.delete(user)            # Delete by object
orm.delete_by_id(User, 2)  # Delete by ID
orm.delete_all(User)       # Delete all records for the class
```

## Limitations

- Supports only simple types (`int`, `str`, `float`).
- Does not support complex queries, relationships, or migrations.
- Assumes classes have an `id` attribute for primary keys.

## License

This project is released under the MIT License.
