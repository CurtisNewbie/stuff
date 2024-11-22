import argparse
import re
import mysql.connector
import mysql.connector.cursor
import sys
import shlex
import pystuff

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
                     f"CREATE TABLE `{table}` ", ddl)

    ddl = re.sub("AUTO_INCREMENT=[0-9]+ ?", "", ddl)

    # ddl = re.sub(
    #     "DEFAULT CHARSET=[a-zA-Z_0-9]+ ?", "", ddl)
    # ddl = re.sub(
    #     "COLLATE=[0-9a-zA-Z_]+ ?", "", ddl)

    ddl = ddl.strip() + ";"

    do_reshape = False
    if do_reshape:
        ddl = reshape(ddl)

    print(f"{ddl}\n")

# TODO: refactor this later
def reshape(ddl: str) -> str:
    indent = [27, 20, 15, 7, 10, 20, 10, 10, 20, 10, 10, 1]
    # tokenize
    lines = ddl.split('\n')
    reshaped = []
    for i in range(len(lines)):
        l = lines[i].strip()
        if i == 0 or i == len(lines) - 1:
            reshaped.append(l)
            continue
        if l.startswith("PRIMARY") or l.startswith("KEY") or l.startswith("UNIQUE"):
            reshaped.append(f"{pystuff.spaces(2)}{l}")
            continue
        if l.startswith("PARTITION") or l.startswith("/*") or l.startswith("(") or l.startswith(")"):
            reshaped.append(l)
            continue

        tokens = shlex.split(l, posix=False)
        filtered = []
        j = 0
        while j < len(tokens):
            if tokens[j] == 'NOT' or tokens[j] == 'DEFAULT':
                filtered.append(tokens[j] + " " + tokens[j + 1])
                j += 2
            elif tokens[j] == ',':
                filtered[len(filtered) - 1] += ","
                j += 1
            elif tokens[j].lower() == 'unsigned':
                filtered[len(filtered) - 1] += " UNSIGNED"
                j += 1
            else:
                filtered.append(tokens[j])
                j += 1

        tokens = filtered
        for k in range(len(tokens)):
            if k < len(tokens) - 1:
                indented = f"{tokens[k]}{pystuff.spaces(indent[k] - pystuff.str_width(tokens[k]))}"
                # print(f"'{tokens[k]}' -> '{indented}'")
                tokens[k] = indented
                if k == 1:
                    tokens[k] = tokens[k].upper()

        reshaped.append("  " + " ".join(tokens))

    return "\n".join(reshaped)


def parsearg():
    ap = argparse.ArgumentParser("ttables.py by Yongj.Zhuang")
    required = ap.add_argument_group('required arguments')
    required.add_argument("-user", '-u', help="username",
                          type=str, required=False, default='root')
    required.add_argument(
        "-database", '-db', help="database name", type=str, required=True)

    ap.add_argument("-password", '-p', help="password (by default it's empty string)",
                    type=str, default="", required=False)
    ap.add_argument(
        "-host", '-ho', help="host (by default it's localhost)", type=str, default="localhost", required=False)
    ap.add_argument(
        "-table", '-t', help="table name (if not specified, all tables' DDL are queried and printed), there can be multiple table names delimited by comma", type=str, required=False)
    ap.add_argument(
        "-inclschema", help="include schema name in CREATE TABLE DDL", action="store_true", required=False)
    ap.add_argument(
        "-debug", help="debug mode", action="store_true", required=False)
    return ap.parse_args()


def debug(callback):
    if isdebug:
        print(callback())


# python3 ttables.py -database acct  | pbcopy
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
            show_create_table(
                cursor, tables[i], database if args.inclschema else None)
    else:
        cursor.execute('show tables')
        resultset: list = cursor.fetchall()

        for i in range(len(resultset)):
            debug(lambda: f"rs {resultset[i][0]}")
            table = str(resultset[i][0])
            debug(lambda: f"table: {table}, i: {i}")
            show_create_table(
                cursor, table, database if args.inclschema else None)

    cursor.close()
    cnx.close()
