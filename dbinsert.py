import argparse
import mysql.connector
import mysql.connector.cursor
import sys


def parsearg():
    ap = argparse.ArgumentParser("dbinsert.py by Yongj.Zhuang")
    required = ap.add_argument_group('required arguments')
    required.add_argument("-user", '-u', help="username",
                          type=str, required=True)
    ap.add_argument("-password", '-p', help="password (by default it's empty string)",
                    type=str, default="", required=False)
    ap.add_argument(
        "-host", help="host (by default it's localhost)", type=str, default="localhost", required=False)
    ap.add_argument(
        "-sql", help="SELECT SQL", type=str, required=True)
    ap.add_argument(
        "-database",  help="database", type=str, required=False, default="")
    ap.add_argument(
        "-table",  help="table", type=str, required=False, default="")
    return ap.parse_args()


"""
python3 -m pip install mysql-connector-python
"""
if __name__ == '__main__':

    args = parsearg()
    config = {
        'user': args.user,
        'password': args.password,
        'host': args.host,
        'database': None,
        'raise_on_warnings': True,
        'connect_timeout': 5000
    }

    cnx: mysql.connector.MySQLConnection = mysql.connector.connect(**config)
    cursor: mysql.connector.cursor.MySQLCursor = cnx.cursor()

    if not args.sql:
        sys.exit(0)

    cursor.execute(args.sql)
    trs: list = cursor.fetchall()

    print(f">> {args.sql}")
    print(f">> {args.database}.{args.table}")
#     print(cursor.column_names)
#     print(trs)
    print()

    built = f"INSERT INTO {args.database}.{args.table} ("
    for i in range(len(cursor.column_names)):
        c = cursor.column_names[i]
        built = built + c
        if i < len(cursor.column_names) - 1:
            built = built + ","
    built = built + ") VALUES"

    rows = []
    for i in range(len(trs)):
        r = trs[i]
        qr = []
        for j in range(len(r)):
            qr.append(f"'{r[j]}'")

        rows.append(",".join(qr))

    for i in range(len(rows)):
        r = rows[i]
        built = built + f"\n  ({r})"
        if i < len(rows) - 1:
            built += ","
    built += ";"

    print(built)
    print()

    cursor.close()
    cnx.close()
