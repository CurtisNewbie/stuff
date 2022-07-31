from genericpath import exists
from io import TextIOWrapper
import xlrd
import sys

# for development only
debug = True

'''
[0] - input path
[1] - output path

yongj.Zhuang
'''
if __name__ == '__main__':

    la = len(sys.argv)
    if la < 3:
        print("\nPlease provide following arguments\n")
        print(" [0] - input path")
        print(" [1] - output path")
        print(" [2] - table name")
        print(" [3] - database name")
        print("\n python3 insertgen.py myexcel.xls generated.sql mytable mydb\n")
        sys.exit(1)

    ip = sys.argv[1]
    op = sys.argv[2]
    tb = sys.argv[3] if la > 3 else None
    db = sys.argv[4] if la > 4 else None

    if debug:
        print(
            f"[debug] input path: '{ip}', output path: '{op}', table name: '{tb}', database: '{db}'")

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

    nheaders = len(headers)

    if debug:
        print(f"[debug] headers: {headers}")

    body: list[list[str]] = []
    # parse body
    for i in range(1, rc):
        r = []
        for j in range(cc):
            r.append(sheet.cell_value(i, j))
        body.append(r)

    if debug:
        print(f"[debug] body: {body}")

    # starts generating the insert sql
    insert = "INSERT INTO "
    if db is not None:
        insert += db

    if tb is not None:
        insert = insert + ("." + tb if db is not None else tb)

    insert += "(" + ",".join(headers) + ") VALUES "

    lbody = len(body)
    for i in range(lbody):
        row = body[i]
        preprocessed = []

        for j in range(nheaders):
            preprocessed.append(f"\"{row[j]}\"")

        insert += "\n(" + ",".join(preprocessed) + ")"
        if i < lbody - 1:
            insert += ","

    insert += ";"

    print(insert)

    f = open(op, "w")
    f.write(insert)
    f.close()
