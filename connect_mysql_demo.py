from mysql.connector import *
from mysql.connector.cursor import *
import datetime

if __name__ == '__main__':

    config = {
        'user': 'scott',
        'password': 'password',
        'host': '127.0.0.1',
        'database': 'employees',
        'raise_on_warnings': True
    }

    cnx: MySQLConnection = connect(**config)

    # for query ---------------------------
    cursor: CursorBase = cnx.cursor()
    cursor.execute("SELECT first_name, last_name, hire_date FROM employees WHERE hire_date BETWEEN %s AND %s",
                   datetime.date(1999, 1, 1), datetime.date(1999, 12, 31))
    for (first_name, last_name, hire_date) in cursor:
        print(
            f"first_name: {first_name}, last_name: {last_name}, hire_date: {hire_date}")
    cursor.close()

    # for execute -------------------------
    cursor: CursorBase = cnx.cursor()
    add_employee = ("INSERT INTO employees "
                    "(first_name, last_name, hire_date, gender, birth_date) "
                    "VALUES (%s, %s, %s, %s, %s)")
    tomorrow = datetime.now().date() + datetime.timedelta(days=1)
    data_employee = ('Geert', 'Vanderkelen', tomorrow,
                     'M', datetime.date(1977, 6, 14))
    cursor.execute(add_employee, data_employee)
    cursor.close()
    cnx.commit()

    cnx.close()
