from genericpath import exists
import xlrd
import sys

debug = False
flags = {"--debug"}


def isnumchar(c: str):
    return (c >= "0" and c <= "9") or c == "."


def isnumber(s: str) -> bool:
    for i in range(len(s)):
        if not isnumchar(s[i]):
            return False
    return True


def quoted(s: str) -> bool:
    return True if s[0] == "'" or s[0] == "'" else False


def escape(s) -> str:
    if not isinstance(s, str):
        s = str(s)

    if s == "":
        return "''"

    if isnumber(s):
        return s

    if not quoted(s):
        return f"'{s}'"

    return s


'''
python3 -m pip install xlrd

[0] - input path
[1] - database/table name
[2] - output path

'--debug' for debug mode

yongj.Zhuang
'''
if __name__ == '__main__':

    la = len(sys.argv)
    if la < 3:
        print("\n updategen.py by Yongj.Zhuang")
        print("\n # Please provide following arguments:\n")
        print(" [0] - input path")
        print(" [1] - database/table name")
        print(" [2] - index of first column for where condition (0 based)")
        print("\n e.g., python3 updategen.py myexcel.xls mytable 2")
        print("\n '--debug' for debug mode")
        print("\n # Example:\n")
        print(" grade | score > |  score <= | age < ")
        print(" ----------------------------------- ")
        print(" A     |    85   |   100     |  25   ")
        print(" B     |    70   |   85      |  25   ")
        print(" C     |    0    |   70      |  25   ")
        print("\n Command: \"python3 updategen.py bbb.xls mytable 1\"")
        print("\n Generated SQL:\n")
        print(" UPDATE mytable SET grade = \"A\" WHERE score >  85 and score <= 100 and age < 25;")
        print(" UPDATE mytable SET grade = \"B\" WHERE score >  70 and score <= 85 and age < 25;")
        print(" UPDATE mytable SET grade = \"C\" WHERE score >  0 and score <= 70 and age < 25;")
        print()
        sys.exit(1)

    ip: str = sys.argv[1]
    tb: str = sys.argv[2]
    firstwhere: int = int(sys.argv[3])

    if firstwhere < 1:
        print(
            f"Found no column for SET statement, because the 'index of first column for where condtion' is set to {firstwhere}")
        sys.exit(1)

    for i in range(3, la):
        c = sys.argv[i]
        if c == "--debug":
            debug = True

    if debug:
        print(
            f"[debug] input path: '{ip}', table name: '{tb}', index of first column for where condition: '{firstwhere}'")

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

    nrow = sheet.nrows
    ncols = sheet.ncols
    if debug:
        print(f"[debug] row count: {nrow}, col count: {ncols}")

    # parse SET statements
    setcols = []
    for i in range(0, firstwhere):
        c = sheet.cell_value(0, i)
        if c:
            setcols.append(c)
    nsetcols = len(setcols)

    if debug:
        print(f"[debug] columns for SET statement: {setcols}")

    # parse WHERE conditions
    wherecols = []
    for i in range(firstwhere, ncols):
        c = sheet.cell_value(0, i)
        if c:
            wherecols.append(c)
    nwherecols = len(wherecols)

    if debug:
        print(f"[debug] columns for WHERE conditions: {wherecols}")

    values: list[list[str]] = []
    # parse body
    for i in range(1, nrow):
        r = []
        for j in range(ncols):
            r.append(sheet.cell_value(i, j))
        values.append(r)

    if debug:
        print(f"[debug] values: {values}")

    # -------
    #
    # starts generating the update sql
    #
    # -------

    sql = ""
    nvalues = len(values)

    for i in range(nvalues):

        update = f"UPDATE {tb} SET "
        row = values[i]

        for k in range(firstwhere):
            if debug:
                print("[debug] preparing SET ", "i:", i, "k:", k, "ncols:",
                      ncols, "firstwhere:", firstwhere, " -> ", row[k])

            update += setcols[k] + " = " + escape(row[k])
            if k < firstwhere - 1:
                update += ", "

        update += " WHERE "
        for j in range(firstwhere, ncols):
            if debug:
                print("[debug] preparing WHERE ", "i:", i,  "j:", j, "ncols:",
                      ncols, "firstwhere:", firstwhere, " -> ", row[j])

            if j < ncols and j > firstwhere:
                update += " and "

            update += wherecols[j - firstwhere] + " " + escape(row[j])

        sql += (update + ";\n")

    print()
    print(sql)
