# Import Flask modules
from flask import Flask, request, render_template
import pyodbc
import os

# Create an object named app
app = Flask(__name__)

database_host = os.getenv('MSSQL_DATABASE_HOST')
database_name = os.getenv('MSSQL_DATABASE')
database_user = os.getenv('MSSQL_USER')
database_password = os.getenv('MSSQL_PASSWORD')

# Create the connection string
conn_string = "Driver=/opt/microsoft/msodbcsql18/lib64/libmsodbcsql-18.2.so.1.1;Server=tcp:sql-01-dev.database.windows.net,1433;Database=phonebook;Uid=ekastar;Pwd=6T!Bdt%t}1uw;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"

conn = pyodbc.connect(conn_string)
cursor = conn.cursor()

# Write a function named `init_phonebook_db` which initializes the phonebook db
def init_phonebook_db():
    query = f'''
    IF OBJECT_ID('dbo.phonebook') IS NULL
    BEGIN
        CREATE TABLE dbo.phonebook (
            id int IDENTITY (1,1) NOT NULL,
            name varchar(100),
            number varchar(100),
            CONSTRAINT PK_id PRIMARY KEY CLUSTERED (id)
        );
    END
    '''

    cursor.execute(query)
    conn.commit()
# Write a function named `insert_person` which inserts person into the phonebook table in the db,
# and returns text info about result of the operation
def insert_person(name, number):
    query = f"SELECT * FROM phonebook WHERE name LIKE '{name.strip().lower()}'"
    cursor.execute(query)
    row = cursor.fetchone()
    if row is not None:
        return f'Person with name {row[1].title()} already exists.'

    insert = f"INSERT INTO phonebook (name, number) VALUES ('{name.strip().lower()}', '{number}')"
    cursor.execute(insert)
    conn.commit()
    return f'Person {name.strip().title()} added to Phonebook successfully'

# Update a person's record in the phonebook table
def update_person(name, number):
    query = f"SELECT * FROM phonebook WHERE name LIKE '{name.strip().lower()}'"
    cursor.execute(query)
    row = cursor.fetchone()
    if row is None:
        return f'Person with name {name.strip().title()} does not exist.'

    update = f"UPDATE phonebook SET number = '{number}' WHERE id = {row[0]}"
    cursor.execute(update)
    conn.commit()

    return f'Phone record of {name.strip().title()} is updated successfully'

# Delete a person record from the phonebook table
def delete_person(name):
    query = f"SELECT * FROM phonebook WHERE name LIKE '{name.strip().lower()}'"
    cursor.execute(query)
    row = cursor.fetchone()
    if row is None:
        return f'Person with name {name.strip().title()} does not exist, no need to delete.'

    delete = f"DELETE FROM phonebook WHERE id = {row[0]}"
    cursor.execute(delete)
    conn.commit()
    return f'Phone record of {name.strip().title()} is deleted from the phonebook successfully'

@app.route('/add', methods=['GET', 'POST'])
def add_record():
    if request.method == 'POST':
        name = request.form['username']
        if name is None or name.strip() == "":
            return render_template('add-update.html', not_valid=True, message='Invalid input: Name cannot be empty', show_result=False, action_name='save', developer_name='Serdar')
        elif name.isdecimal():
            return render_template('add-update.html', not_valid=True, message='Invalid input: Name of person should be text', show_result=False, action_name='save', developer_name='Serdar')

        phone_number = request.form['phonenumber']
        if phone_number is None or phone_number.strip() == "":
            return render_template('add-update.html', not_valid=True, message='Invalid input: Phone number cannot be empty', show_result=False, action_name='save', developer_name='Serdar')
        elif not phone_number.isdecimal():
            return render_template('add-update.html', not_valid=True, message='Invalid input: Phone number should be in numeric format', show_result=False, action_name='save', developer_name='Serdar')

        result = insert_person(name, phone_number)
        return render_template('add-update.html', show_result=True, result=result, not_valid=False, action_name='save', developer_name='Serdar')
    else:
        return render_template('add-update.html', show_result=False, not_valid=False, action_name='save', developer_name='Serdar')

@app.route('/update', methods=['GET', 'POST'])
def update_record():
    if request.method == 'POST':
        name = request.form['username']
        if name is None or name.strip() == "":
            return render_template('add-update.html', not_valid=True, message='Invalid input: Name cannot be empty', show_result=False, action_name='update', developer_name='Serdar')
        phone_number = request.form['phonenumber']
        if phone_number is None or phone_number.strip() == "":
            return render_template('add-update.html', not_valid=True, message='Invalid input: Phone number cannot be empty', show_result=False, action_name='update', developer_name='Serdar')
        elif not phone_number.isdecimal():
            return render_template('add-update.html', not_valid=True, message='Invalid input: Phone number should be in numeric format', show_result=False, action_name='update', developer_name='Serdar')

        result = update_person(name, phone_number)
        return render_template('add-update.html', show_result=True, result=result, not_valid=False, action_name='update', developer_name='Serdar')
    else:
        return render_template('add-update.html', show_result=False, not_valid=False, action_name='update', developer_name='Serdar')

@app.route('/delete', methods=['GET', 'POST'])
def delete_record():
    if request.method == 'POST':
        name = request.form['username']
        if name is None or name.strip() == "":
            return render_template('delete.html', not_valid=True, message='Invalid input: Name cannot be empty', show_result=False, developer_name='Serdar')
        result = delete_person(name)
        return render_template('delete.html', show_result=True, result=result, not_valid=False, developer_name='Ccseyhan')
    else:
        return render_template('delete.html', show_result=False, not_valid=False, developer_name='Ccseyhan')

@app.route('/', methods=['GET', 'POST'])
def find_records():
    return render_template('index.html', show_result=False, developer_name='Serdar')

if __name__ == '__main__':
    init_phonebook_db()
    app.run(host='0.0.0.0', port=80)
