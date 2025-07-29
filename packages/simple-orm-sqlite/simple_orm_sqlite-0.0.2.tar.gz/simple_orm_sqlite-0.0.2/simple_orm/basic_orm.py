import sqlite3

class SimpleORM:
    def __init__(self, db_name: str) -> None:
        self.conn =  sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def create_table(self, cls) -> None:
        columns = []
        for name, typ in cls.__annotations__.items():
            if name == 'id':
                columns.append("id INTEGER PRIMARY KEY AUTOINCREMENT")
            else:
                columns.append(f"{name} {self.python_type_to_sql(typ)}")

        columns_def = ", ".join(columns)
        sql = f"CREATE TABLE IF NOT EXISTS {cls.__name__.lower()}s ({columns_def})"
        self.cursor.execute(sql)
        self.conn.commit()

    def insert(self, obj) -> None:
        columns = []
        values = []
        for name in obj.__annotations__:
            if name != "id":
                columns.append(name)
                values.append(getattr(obj, name))
        cols = ", ".join(columns)
        placeholders = ", ".join("?" for _ in columns)
        sql = f"INSERT INTO {obj.__class__.__name__.lower()}s ({cols}) VALUES ({placeholders})"
        self.cursor.execute(sql, values)
        self.conn.commit()
        obj.id = self.cursor.lastrowid

    def get_all(self, cls) -> list:
        sql = f"SELECT * FROM {cls.__name__.lower()}s"
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        results = []
        for row in rows:
            obj = object.__new__(cls)
            for i, key in enumerate(cls.__annotations__):
                setattr(obj, key, row[i])
            results.append(obj)
        return results
    
    def get_one(self, cls, obj_id: int) -> None:
        table_name = cls.__name__.lower() + "s"
        sql = f"SELECT * FROM {table_name} WHERE id = ?"
        self.cursor.execute(sql, (obj_id,))
        row = self.cursor.fetchone()
        if row is None:
            return None
        obj = object.__new__(cls)
        for i, key in enumerate(cls.__annotations__):
            setattr(obj, key, row[i])
        return obj

    
    def delete(self, obj) -> None:
        table_name = obj.__class__.__name__.lower() + "s"
        sql = f"DELETE FROM {table_name} WHERE id = ?"
        self.cursor.execute(sql, (obj.id,))
        self.conn.commit()

    def delete_by_id(self, cls, obj_id: int) -> None:
        table_name = cls.__name__.lower() + "s"
        sql = f"DELETE FROM {table_name} WHERE id = ?"
        self.cursor.execute(sql, (obj_id,))
        self.conn.commit()

    def delete_all(self, cls) -> None:
        table_name = cls.__name__.lower() + "s"
        sql = f"DELETE FROM {table_name}"
        self.cursor.execute(sql)
        self.conn.commit()

    
    def python_type_to_sql(self, typ: str | int | float) -> str:
        if typ == int:
            return "INTEGER"
        elif typ == str:
            return "TEXT"
        elif typ == float:
            return "REAL"
        else:
            return "TEXT"
