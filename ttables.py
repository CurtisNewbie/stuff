import argparse
import re
import mysql.connector
import mysql.connector.cursor
import sys

isdebug = False


def show_create_table(cursor, table, database):
    """
    print SHOW CREATE TABLE DDL 

    database name is excluded if it's absent, else if it's present, it will be concatenated to 
    the table name, e.g., 'some_db.some_table'
    """

    cursor.execute(f'show create table {table}')
    trs: list = cursor.fetchall()
    ddl = trs[0][1]
    debug(lambda: f"original ddl: {ddl}")

    if database:
        ddl = re.sub("CREATE TABLE `[a-zA-Z_]+` ",
                     f"CREATE TABLE IF NOT EXISTS {database}.{table} ", ddl)
    else:
        ddl = re.sub("CREATE TABLE `[a-zA-Z_]+` ",
                     f"CREATE TABLE IF NOT EXISTS {table} ", ddl)

    ddl = re.sub(
        "DEFAULT CHARSET=[a-zA-Z_0-9]+ AUTO_INCREMENT=[0-9]+ ?", "", ddl)
    ddl = re.sub(
        "DEFAULT CHARSET=[a-zA-Z_0-9]+ ?", "", ddl)
    ddl = re.sub(
        "COLLATE=[0-9a-zA-Z_]+ ?", "", ddl)
    ddl = ddl.strip() + ";"
    print(f"{ddl}\n")


def parsearg():
    ap = argparse.ArgumentParser("ttables.py by Yongj.Zhuang")
    required = ap.add_argument_group('required arguments')
    required.add_argument("-user", '-u', help="username", type=str, required=True)
    required.add_argument(
        "-database", '-db', help="database name", type=str, required=True)

    ap.add_argument("-password", '-p', help="password (by default it's empty string)",
                    type=str, default="", required=False)
    ap.add_argument(
        "-host", '-ho', help="host (by default it's localhost)", type=str, default="localhost", required=False)
    ap.add_argument(
        "-table", '-t', help="table name (if not specified, all tables' DDL are queried and printed), there can be multiple table names delimited by comma", type=str, required=False)
    ap.add_argument(
        "-exclschema", help="exclude schema name in CREATE TABLE DDL", action="store_true", required=False)
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
        tables = str.split(args.table, ",")
    else:
        tables = []

    if len(tables) > 0:
        for i in range(len(tables)):
            debug(lambda: f"i: {i}, table: {tables[i]}")
            show_create_table(cursor, tables[i], None if args.exclschema else database)
    else:
        cursor.execute('show tables')
        resultset: list = cursor.fetchall()

        for i in range(len(resultset)):
            debug(lambda: f"rs {resultset[i][0]}")
            table = str(resultset[i][0])
            debug(lambda: f"table: {table}, i: {i}")
            show_create_table(
                cursor, table, None if args.exclschema else database)

    cursor.close()
    cnx.close()
