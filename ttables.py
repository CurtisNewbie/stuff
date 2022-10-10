import argparse
import re
import mysql.connector
import mysql.connector.cursor
import sys

isdebug = False


def show_create_table(cursor, table, database):
    cursor.execute(f'show create table {table}')
    trs: list = cursor.fetchall()
    ddl = trs[0][1]

    ddl = re.sub("CREATE TABLE `[a-zA-Z_]+` ",
                 f"CREATE TABLE IF NOT EXISTS {database}.{table} ", ddl)

    ddl = re.sub(
        "AUTO_INCREMENT=[0-9]+ DEFAULT CHARSET=[0-9a-zA-Z]+ ", "", ddl)
    ddl = ddl + ";"
    print(f"{ddl}\n")


def parsearg():
    ap = argparse.ArgumentParser("ttables.py by Yongj.Zhuang")
    required = ap.add_argument_group('required arguments')
    required.add_argument("-user", help="username", type=str, required=True)
    required.add_argument(
        "-database", help="database name", type=str, required=True)

    ap.add_argument("-password", help="password (by default it's empty string)",
                    type=str, default="", required=False)
    ap.add_argument(
        "-host", help="host (by default it's localhost)", type=str, default="localhost", required=False)
    ap.add_argument(
        "-table", help="table name (if not specified, all tables' DDL are queried and printed)", type=str, required=False)
    ap.add_argument(
        "-debug", help="debug mode", action="store_true", required=False)
    return ap.parse_args()


def debug(callback):
    if isdebug:
        print(callback())


if __name__ == '__main__':

    args = parsearg()
    isdebug = args.debug

    debug(lambda: f"args: {sys.argv}, parsed: {args}")
    argdict: dict[str, str] = {}
    database = args.database

    config = {
        'user': args.user,
        'password': args.password,
        'host': args.host,
        'database': database,
        'raise_on_warnings': True,
        'connect_timeout': 5000
    }
    debug(lambda: f"config: {config}")

    cnx: mysql.connector.MySQLConnection = mysql.connector.connect(**config)
    cursor: mysql.connector.cursor.MySQLCursor = cnx.cursor()
    debug(lambda: f"database connected")

    if args.table:
        show_create_table(cursor, args.table, database)
    else:
        cursor.execute('show tables')
        resultset: list = cursor.fetchall()

        for i in range(len(resultset)):
            debug(lambda: f"rs {resultset[i][0]}")
            table = str(resultset[i][0])
            debug(lambda: f"table: {table}, i: {i}")
            show_create_table(cursor, table, database)

    cursor.close()
    cnx.close()
