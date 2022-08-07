import mysql.connector
import mysql.connector.cursor
import sys

flag: set[str] = {'-excl-default'}
isdebug = False


def isflag(s: str):
    return s in flag


def printhelp():
    print("\ntfields.py by Yongj.Zhuang\n")
    print(" -user username")
    print(" -password password")
    print(" -host host (by default it's localhost)")
    print(" -database database name (optional if table name includes the database)")
    print(" -table table name")
    print(" -excl-default exclude columns with default value")
    print("\n e.g., python3 tfields.py -user root -password '123456' -host 192.168.10.1 -table mydb.mytable -excl-default\n")


def debug(callback):
    if isdebug:
        print(callback())


def getdefault(argdict, key, default):
    return argdict[key] if key in argdict else default


def getrequired(argdict, key):
    if key in argdict:
        return argdict[key]
    print(f"Missing argument: '{key}'")
    sys.exit(1)


if __name__ == '__main__':
    args = sys.argv[1:]
    nargs = len(args)
    if nargs < 1:
        printhelp()
        sys.exit(1)

    debug(lambda: f"args: {args}")

    argdict: dict[str, str] = {}

    i = 0
    while i < nargs:
        k = str(args[i])
        if isflag(k):
            argdict[k] = True
            i += 1
            continue

        if i + 1 >= nargs:
            debug(lambda: f"missing arguments, i: {i}, nargs: {nargs}")
            print(f"missing value after argument: '{k}'")
            sys.exit(1)

        va = args[i + 1]
        argdict[k] = str(va)
        i += 2

    debug(lambda: f"argdict: {argdict}")

    table: str = getrequired(argdict, "-table")
    database = None

    j = table.find('.')
    if j > -1:
        if j > 0:
            database = table[0: j]
        table = table[j + 1:]

    if database is None:
        database = getrequired(argdict, "-database")

    config = {
        'user': getrequired(argdict, "-user"),
        'password': getrequired(argdict, "-password"),
        'host': getdefault(argdict, "-host", 'localhost'),
        'database': database,
        'raise_on_warnings': True,
        'connect_timeout': 1000
    }
    debug(lambda: f"config: {config}")

    cnx: mysql.connector.MySQLConnection = mysql.connector.connect(**config)
    cursor: mysql.connector.cursor.MySQLCursor = cnx.cursor()
    debug(lambda: f"database connected")

    debug(lambda: f"reading table {table} schema")

    cursor.execute(f'DESCRIBE {table}')

    resultset: list = cursor.fetchall()
    columns: tuple = cursor.column_names
    debug(lambda: f"columns: {columns}")
    debug(lambda: f"result set: {resultset}")

    cursor.close()
    cnx.close()

    exclidx = -1
    for i in range(len(columns)):
        c = str(columns[i])
        if c.lower() == 'default':
            exclidx = i
            break

    excldef = getdefault(argdict, '-excl-default', False) and exclidx > -1
    debug(lambda: f"excluding column with default values")

    fields = []
    for i in range(len(resultset)):
        n = resultset[i][0]
        dv = resultset[i][exclidx]
        if excldef and dv != None:
            debug(lambda: f"column '{n}' has default value '{dv}', skipped")
            continue
        fields.append(n)

    debug(lambda: f"fields: {fields}")

    print(f"\nParsed {database}.{table}")

    print("\ndelimited by ',':\n")
    print(",".join(fields))
    print("\ndelimited by tab:\n")
    print("\t".join(fields))
    print()
