import sqlite3
import pytest
from queries import insert_rows, update_row, delete_row
from dataclasses import dataclass

@dataclass
class Person:
    id: int
    name: str
    age: int
    
@pytest.fixture
def cur():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE Person (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)")
    cur = conn.cursor()
    yield cur
    conn.close()


def test_insert_rows(cur):
    objs = [Person(id=1, name="Alice", age=30), Person(id=2, name="Bob", age=25)]
    count = insert_rows(cur, "Person", ["id", "name", "age"], objs)
    assert count == 2
    
    rows = cur.execute("SELECT id, name, age FROM person ORDER BY id").fetchall()
    assert rows == [(1, "Alice", 30), (2, "Bob", 25)]
    

def test_update_row(cur):
    cur.execute("INSERT INTO person (id, name, age) VALUES (1, 'Kafka', 30)")
    kafka = Person(id=1, name="Kafka Smith", age=20)
    affected_rows = update_row(cur, "Person", ["name", "age"], "id", kafka)
    assert affected_rows == 1

    row = cur.execute("SELECT id, name, age FROM person WHERE id=1").fetchone()
    assert row == (1, "Kafka Smith", 20)


def test_delete_row(cur):
    cur.execute("INSERT INTO person (id, name, age) VALUES (1, 'Kafka', 30)")
    affected_rows = delete_row(cur, "Person", "id", 1)
    assert affected_rows == 1

    row = cur.execute("SELECT id, name, age FROM person WHERE id=1").fetchone()
    assert row is None
    
