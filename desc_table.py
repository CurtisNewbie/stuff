import os
import mysql.connector
import mysql.connector.cursor
import argparse
import pystuff


def desc_table(cursor, table, comments) -> str:
    cursor.execute(f'desc {table}')
    trs: list = cursor.fetchall()
    col = list(cursor.column_names)

    col_idx = {}
    for i in range(len(col)):
        col_idx[col[i]] = i

    col.append("Comment")
    ctrs = []
    for r in trs:
        r = list(r)
        table = table
        field = r[col_idx['Field']]
        r.append(comments[table + '.' + field])
        ctrs.append(r)
    return f"\n-- {table}\n{pystuff.print_table(col, ctrs, False, set(['Null', 'Key', 'Default', 'Extra']))}"

def parsearg():
    ap = argparse.ArgumentParser("desc_table.py by Yongj.Zhuang")
    required = ap.add_argument_group('required arguments')
    required.add_argument("-user", '-u', help="username", type=str, required=True)
    required.add_argument("-database", '-db', help="database name", type=str, required=True)

    ap.add_argument("-password", '-p', help="password (by default it's empty string)", type=str, default="", required=False)
    ap.add_argument("-host", '-ho', help="host (by default it's localhost)", type=str, default="localhost", required=False)
    return ap.parse_args()


if __name__ == '__main__':

    args = parsearg()
    database = args.database

    config = {
        'user': args.user,
        'password': args.password,
        'host': args.host,
        'database': database,
        'raise_on_warnings': True,
        'connect_timeout': 5000
    }

    cnx: mysql.connector.MySQLConnection = mysql.connector.connect(**config)
    cursor: mysql.connector.cursor.MySQLCursor = cnx.cursor()

    cursor.execute(f'select * from information_schema.columns where table_schema = \'{database}\'')
    resultset: list = cursor.fetchall()
    comments = {}

    col_idx = {}
    cn = cursor.column_names
    for i in range(len(cn)):
        col_idx[cn[i]] = i

    for r in resultset:
        comments[r[col_idx['TABLE_NAME']] + "." + r[col_idx['COLUMN_NAME']]] = r[col_idx['COLUMN_COMMENT']]

    cursor.execute('show tables')
    resultset: list = cursor.fetchall()

    outputs = []
    for i in range(len(resultset)):
        table = str(resultset[i][0])
        outputs.append(desc_table(cursor, table, comments))

    cursor.close()
    cnx.close()

    with open(f'desc_{database}_{table}.log', 'w') as f:
        f.write("\n".join(outputs))
