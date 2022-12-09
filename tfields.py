import argparse
import mysql.connector
import mysql.connector.cursor
import sys

isdebug = False


def parsearg():
    ap = argparse.ArgumentParser("tfields.py by Yongj.Zhuang")
    ap.add_argument("-user", help="username", type=str, required=True)
    ap.add_argument("-password", help="password",
                    type=str, default="", required=False)
    ap.add_argument(
        "-host", help="host (by default it's localhost)", type=str, default="localhost", required=False)
    ap.add_argument("-database",
                    help="database, optional if it's already included in the table name", type=str,  default="", required=False)
    ap.add_argument(
        "-table", help="table name (may include database name)")
    ap.add_argument(
        "-excldefault", help="exclude columns with default value", action="store_true", required=False)
    ap.add_argument(
        "-exclcol", help="exclude columns, delimited by comma", default="", required=False)
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
    table: str = args.table
    database = None

    j = table.find('.')
    if j > -1:
        if j > 0:
            database = table[0: j]
        table = table[j + 1:]

    if database is None:
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

    debug(lambda: f"args.excldefault: {args.excldefault}")
    excldef = args.excldefault and exclidx > -1
    debug(lambda: f"excluding column with default values")

    excluded: set[str] = set()
    if args.exclcol != "":
        cols: list[str] = str(args.exclcol).split(",")
        excluded = set(cols)
    debug(lambda: f"columns specified in -exclcol {excluded}")

    fields = []
    for i in range(len(resultset)):
        n = resultset[i][0]
        defaultval = resultset[i][exclidx] # column for default value
        if excldef and defaultval != None:
            debug(
                lambda: f"column '{n}' has default value '{defaultval}', skipped")
            continue
        if n in excluded:
            debug(lambda: f"column '{n}' is excluded")
            continue
        fields.append(n)

    debug(lambda: f"fields: {fields}")

    print(f"\nParsed {database}.{table}")

    print("\ndelimited by ',':\n")
    print(",".join(fields))
    print("\ndelimited by tab:\n")
    print("\t".join(fields))
    print("\ndelimited by space:\n")
    print(" ".join(fields))
    print()
