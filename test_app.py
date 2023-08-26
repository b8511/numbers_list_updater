import json
import sqlite3
import asyncio
import threading
import websockets
from flask import Flask, render_template, jsonify

app = Flask(__name__)

# Create a lock for database access
db_lock = threading.Lock()


# Function to get a new database connection and cursor
def get_db_cursor():
    db_connection = sqlite3.connect("number_list.db")
    return db_connection, db_connection.cursor()


# Initialize the database with initial values
def initialize_database():
    with db_lock:
        db_connection, db_cursor = get_db_cursor()

        # Check if the table exists
        db_cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='numbers'"
        )
        table_exists = db_cursor.fetchone()

        if not table_exists:
            # Create the table
            db_cursor.execute("CREATE TABLE numbers (value INTEGER PRIMARY KEY)")
            db_connection.commit()

            # Insert initial values
            initial_values = [
                (0,),
                (1,),
                (2,),
                (3,),
                (4,),
                (5,),
                (6,),
                (7,),
                (8,),
                (9,),
                (10,),
            ]
            db_cursor.executemany(
                "INSERT INTO numbers (value) VALUES (?)", initial_values
            )
            db_connection.commit()


@app.route("/")
def index():
    with db_lock:
        db_connection, db_cursor = get_db_cursor()
        db_cursor.execute("SELECT value FROM numbers")
        rows = db_cursor.fetchall()
        number_list = [row[0] for row in rows]
        return render_template("index.html", number_list=number_list)


@app.route("/get_number_list")
def get_number_list():
    with db_lock:
        db_connection, db_cursor = get_db_cursor()
        db_cursor.execute("SELECT value FROM numbers")
        rows = db_cursor.fetchall()
        number_list = [row[0] for row in rows]
        db_cursor.close()  # Close the cursor
        db_connection.close()  # Close the connection
        return jsonify({"number_list": number_list})


async def manage_list(websocket):
    async for message in websocket:
        try:
            message = json.loads(message)
            msg_type, number = message
            number = int(number)
            if msg_type == "add_new_item":
                add_number_to_db(number)
            elif msg_type == "deleted_item":
                remove_number_from_db(number)
            else:
                print("Invalid operation or number already exists/doesn't exist")
        except Exception as e:
            print(f"Invalid message format. ERROR: {e}")


def add_number_to_db(number):
    with db_lock:
        db_connection, db_cursor = get_db_cursor()
        try:
            db_cursor.execute(
                "INSERT INTO numbers (value) VALUES (?) ON CONFLICT DO NOTHING",
                (number,),
            )
            db_connection.commit()
            print(f"Added {number} to the list in the database.")
        except sqlite3.IntegrityError:
            print(f"Number {number} is already in the list in the database.")
        finally:
            db_cursor.close()  # Close the cursor
            db_connection.close()  # Close the connection


def remove_number_from_db(number):
    with db_lock:
        db_connection, db_cursor = get_db_cursor()
        db_cursor.execute("DELETE FROM numbers WHERE value = ?", (number,))
        db_connection.commit()
        db_cursor.close()  # Close the cursor
        db_connection.close()  # Close the connection
        print(f"Removed {number} from the list in the database.")


async def main():
    # Initialize the database structure and populate with initial values
    initialize_database()

    async with websockets.connect("ws://localhost:8765/") as websocket:
        await manage_list(websocket)


if __name__ == "__main__":
    asyncio.run(main())
