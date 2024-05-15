import re
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
    return ap.parse_args()

def extract_schema_table(sql: str) -> tuple[str]:
    res = re.search(r"^select .* from ([^ \.]+).([^ \.;]+).*$", sql, re.IGNORECASE)
    return res.group(1), res.group(2)


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
    rs: list = cursor.fetchall()

    # print(f">> {args.sql}")
    schema, table = extract_schema_table(args.sql)

    # print(f">> will query {schema}.{table}")
    # print()

    excl_cols = ['id']
    excl_idx = []

    built = f"INSERT INTO {schema}.{table} ("
    for i in range(len(cursor.column_names)):
        c = cursor.column_names[i]
        if c in excl_cols:
            excl_idx.append(i)
            continue

        built = built + c
        if i < len(cursor.column_names) - 1:
            built = built + ","
    built = built + ") VALUES"


    rows = []
    for i in range(len(rs)):
        r = rs[i]
        qr = []
        for j in range(len(r)):
            if j in excl_idx: continue
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
