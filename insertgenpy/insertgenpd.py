from genericpath import exists
import sys
import os
from typing import Callable
import pandas

isdebug = False
mute = False
flags = {"--debug", "--mute"}
keywords: set[str] = {"current_timestamp", "now()"}
env_default_values_key = "INSERTGEN_DEFAULT"


def issqlkeyword(w: any) -> bool:
    '''
    check if the word is a sql keyword
    '''
    lw = str(w).lower()
    iskw = lw in keywords
    debug(lambda: f"word: '{w}' is keyword: {iskw}")
    return iskw


def debug(callback: Callable[[], str]):
    '''
    print debug log, only if 'isdebug' = True
    '''
    if isdebug:
        print("[debug] " + callback())


def isnumchar(c: str):
    '''
    check if the given character is a number character (0-9 or '.')
    '''
    return (c >= "0" and c <= "9") or c == "."


def isnumber(s: str) -> bool:
    '''
    check if the given string is actually a number ([0-9.]+)
    '''
    if not s:
        return False
    for i in range(len(s)):
        if not isnumchar(s[i]):
            return False
    return True


def quoted(s: str) -> bool:
    if not s:
        return False
    if len(s) < 2:
        return False
    return True if (s[0] == "'" or s[len(s) - 1] == "'") or (s[0] == "\"" or s[len(s) - 1] == "\"") else False


def escape(w) -> str:
    '''
    escape word
    '''
    if pandas.isnull(w):
        ec = "''"
        debug(
            lambda: f"escaping word: '{w}', type: '{type(w)}', escaped: {ec}")
        return ec

    w = str(w)
    if quoted(w) or issqlkeyword(w):
        ec = w
    else:
        ec = "\"" + w.replace('\'', '\\\'').replace('\"', '\\\"') + "\""

    debug(lambda: f"escaping word: '{w}', type: '{type(w)}', escaped: {ec}")
    return ec


'''
python3 -m pip install pandas openpyxl 

(openpyxl is optional, it's used for *.xlsx files)

[0] - input path
[1] - database/table name
[2] - output path

'--debug' for debug mode
'--mute' for not printing the generated sql on console

Environmnet variable:

'INSERTGEN_DEFAULT=...' specify the default column and value

Yongj.Zhuang
'''
if __name__ == '__main__':

    la = len(sys.argv)
    if la < 2:
        print("\n insertgenpd.py (pandas) by Yongj.Zhuang")
        print("\n Please provide following arguments:\n")
        print(" [0] - input path")
        print(" [1] - database/table name")
        print(" [2] - output path (optional)")
        print("\n e.g., python3 insertgen.py myexcel.xls generated.sql mytable")
        print("\n '--debug' for debug mode")
        print("\n '--mute' for not printing the generated sql on console")
        print("\n 'INSERTGEN_DEFAULT' environment variable for sepcifying the default columns and values")
        print(
            "\n e.g., INSERTGEN_DEFAULT=\"created_at=CURRENT_TIMESTAMP,created_by=SYSTEM\"")
        print("\n For values in excel, always \"\" instead of ''")
        print()
        sys.exit(1)

    ip = sys.argv[1]
    tb = sys.argv[2]
    op = sys.argv[3] if la > 3 and sys.argv[3] not in flags else None

    for i in range(2, la):
        v = sys.argv[i]
        if v == "--debug":
            isdebug = True
        elif v == '--mute':
            mute = True

    # parse default columns and values
    defkv = os.environ.get(env_default_values_key)
    defk = []
    defv = []
    if defkv is not None:
        tokens = defkv.split(",")
        for i in range(len(tokens)):
            ts = tokens[i].split("=")
            defk.append(ts[0])
            defv.append("''" if len(ts) < 1 else ts[1])

    debug(lambda: f"defaultkv: '{defkv}'")
    debug(lambda: f"default columns: {defk}")
    debug(lambda: f"default values: {defv}")
    debug(
        lambda: f"input path: '{ip}', output path: '{op}', table name: '{tb}'")

    # read and parse workbook
    if not exists(ip):
        print(f"Input file '{ip}' not found")
        sys.exit(1)

    df: pandas.DataFrame = pandas.read_excel(ip, 0)
    debug(lambda: f"opened workbook '{ip}', content: '{df}'")

    nrow = len(df)
    ncol = len(df.columns)
    debug(lambda: f"row count: {nrow}, col count: {ncol}")

    ncolmap = {}
    # parse header
    headers = []
    for i in range(ncol):
        h = df.columns[i]
        if not h:
            break
        headers.append(str(h))
    debug(lambda: f"Last column is {headers[len(headers)-1]}")

    debug(lambda: f"Start appending default columns")
    for i in range(len(defk)):
        headers.append(defk[i])
    nheaders = len(headers)
    debug(lambda: f"final headers: {headers}")

    body: list[list[str]] = []
    # parse body
    for i in range(nrow):
        r = []
        for j in range(ncol):
            r.append(df.iat[i, j])
        for k in range(len(defv)):
            r.append(defv[k])
        body.append(r)
    debug(lambda: f"body: {body}")

    # -------
    #
    # starts generating the insert sql
    #
    # -------

    insert = "INSERT INTO "

    if tb is not None:
        insert = insert + tb

    insert += "(" + ",".join(headers) + ") VALUES "

    lbody = len(body)
    for i in range(lbody):
        row = body[i]
        preprocessed = []

        for j in range(nheaders):
            w = escape(row[j])
            preprocessed.append(w)

        insert += "\n  (" + ",".join(preprocessed) + ")"
        if i < lbody - 1:
            insert += ","

    insert += ";"

    if not mute:
        print(insert)

    if op is not None:
        f = open(op, "w")
        f.write(insert)
        f.close()
