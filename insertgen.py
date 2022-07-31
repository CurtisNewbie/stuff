from genericpath import exists
import xlrd
import sys
import os

debug = False
mute = False
flags = {"--debug", "--mute"}
keywords: list[str] = ["CURRENT_TIMESTAMP", "NOW()"]
env_default_values_key = "INSERTGEN_DEFAULT"


# check if w is a sql keyword
def issqlkeyword(w: any) -> bool:
    lw = str(w).lower()
    for i in range(len(keywords)):
        if keywords[i].lower() == lw:
            return True
    return False


'''
python3 -m pip install xlrd

[0] - input path
[1] - database/table name
[2] - output path

'--debug' for debug mode
'--mute' for not printing the generated sql on console

Environmnet variable: 

'INSERTGEN_DEFAULT=...' specify the default column and value

yongj.Zhuang
'''
if __name__ == '__main__':

    la = len(sys.argv)
    if la < 2:
        print("\n insertgen.py by Yongj.Zhuang")
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
        print()
        sys.exit(1)

    ip = sys.argv[1]
    tb = sys.argv[2]
    op = sys.argv[3] if la > 3 and sys.argv[3] not in flags else None

    for i in range(2, la):
        v = sys.argv[i]
        if v == "--debug":
            debug = True
        elif v == '--mute':
            mute = True

    # parse default columns and values
    defaultenv = os.environ.get(env_default_values_key)
    defaultk = []
    defaultv = []
    if defaultenv is not None:
        tokens = defaultenv.split(",")
        for i in range(len(tokens)):
            ts = tokens[i].split("=")
            defaultk.append(ts[0])
            defaultv.append("\"\"" if len(ts) < 1 else ts[1])

    if debug:
        print(
            f"[debug] default env: '{defaultenv}', columns: {defaultk}, values: {defaultv}")
        print(
            f"[debug] input path: '{ip}', output path: '{op}', table name: '{tb}'")

    # read and parse workbook
    if not exists(ip):
        print(f"Input file '{ip}' not found")
        sys.exit(1)

    book: "xlrd.book.Book" = xlrd.open_workbook(ip)
    if debug:
        print(f"[debug] opened workbook '{ip}', has '{book.nsheets}' sheets")

    if book.nsheets < 1:
        print(f"opened workbook '{ip}', but it's empty")
        sys.exit(1)

    # we only parse the first sheet
    sheet: "xlrd.sheet.Sheet" = book.sheet_by_index(0)

    rc = sheet.nrows
    cc = sheet.ncols
    if debug:
        print(f"[debug] row count: {rc}, col count: {cc}")

    # parse header
    headers = []
    for i in range(cc):
        h = sheet.cell_value(0, i)
        if h:
            headers.append(h)
    for i in range(len(defaultk)):
        headers.append(defaultk[i])
    nheaders = len(headers)

    if debug:
        print(f"[debug] headers: {headers}")

    body: list[list[str]] = []
    # parse body
    for i in range(1, rc):
        r = []
        for j in range(cc):
            r.append(sheet.cell_value(i, j))
        for k in range(len(defaultv)):
            r.append(defaultv[k])
        body.append(r)

    if debug:
        print(f"[debug] body: {body}")

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
            w = f"{row[j]}" if issqlkeyword(row[j]) else f"\"{row[j]}\""
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
