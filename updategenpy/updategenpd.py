from genericpath import exists
import sys
from typing import Callable
import pandas

isdebug = False
keywords: set[str] = {"current_timestamp", "now()"}


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

Yongj.Zhuang
'''
if __name__ == '__main__':

    la = len(sys.argv)
    if la < 3:
        print("\n updategen.py by Yongj.Zhuang")
        print("\n # Please provide following arguments:\n")
        print(" [0] - input path")
        print(" [1] - database/table name")
        print(" [2] - name of first where column (must be exactly the same)")
        print("\n e.g., python3 updategen.py myexcel.xls mytable 2")
        print("\n '--debug' for debug mode")
        print("\n # Example:\n")
        print(" grade | score > |  score <= | age < ")
        print(" ----------------------------------- ")
        print(" A     |    85   |   100     |  25   ")
        print(" B     |    70   |   85      |  25   ")
        print(" C     |    0    |   70      |  25   ")
        print("\n Command: \"python3 updategen.py bbb.xls mytable 'score > '\"")
        print("\n Generated SQL:\n")
        print(" UPDATE mytable SET grade = \"A\" WHERE score >  85 and score <= 100 and age < 25;")
        print(" UPDATE mytable SET grade = \"B\" WHERE score >  70 and score <= 85 and age < 25;")
        print(" UPDATE mytable SET grade = \"C\" WHERE score >  0 and score <= 70 and age < 25;")
        print()
        sys.exit(1)

    ip: str = sys.argv[1]
    tb: str = sys.argv[2]
    firstwherename: str = sys.argv[3]

    for i in range(3, la):
        c = sys.argv[i]
        if c == "--debug":
            isdebug = True

    debug(
        lambda: f"input path: '{ip}', table name: '{tb}', name of first WHERE column: '{firstwherename}'")

    # read and parse workbook
    if not exists(ip):
        print(f"Input file '{ip}' not found")
        sys.exit(1)

    df: pandas.DataFrame = pandas.read_excel(ip, 0)
    debug(lambda: f"opened workbook '{ip}', content: '{df}'")

    nrow = len(df)
    ncols = len(df.columns)
    debug(lambda: f"row count: {nrow}, col count: {ncols}")

    # find the first WHERE condition
    firstwhere: int = -1
    for i in range(ncols):
        c = df.columns[i]
        if c and str(c) == firstwherename:
            firstwhere = i
            break
    if firstwhere < 1:
        print(f"unable to find column '{firstwherename}'")
        sys.exit(1)
    debug(lambda: f"found first WHERE condition at {firstwhere}")

    # parse SET statements
    setcols = []
    for i in range(0, firstwhere):
        c = df.columns[i]
        if c:
            setcols.append(c)
    nsetcols = len(setcols)

    debug(lambda: f"columns for SET statement: {setcols}")

    # parse WHERE conditions
    wherecols = []
    for i in range(firstwhere, ncols):
        c = df.columns[i]
        if c:
            wherecols.append(c)
    nwherecols = len(wherecols)

    debug(lambda: f"columns for WHERE conditions: {wherecols}")

    values: list[list[str]] = []
    # parse body
    for i in range(nrow):
        r = []
        for j in range(ncols):
            r.append(df.iat[i, j])
        values.append(r)

    debug(lambda: f"values: {values}")

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
            debug(
                lambda: f"preparing SET i: {i} k: {k} ncols: {ncols} firstwhere: {firstwhere} -> {row[k]}")

            update += setcols[k] + " = " + escape(row[k])
            if k < firstwhere - 1:
                update += ", "

        update += " WHERE "
        for j in range(firstwhere, ncols):
            debug(
                lambda: f"preparing WHERE i: {i} j: {j} ncols: {ncols} firstwhere: {firstwhere} -> {row[j]}")

            if j < ncols and j > firstwhere:
                update += " and "

            update += wherecols[j - firstwhere] + " " + escape(row[j])

        sql += (update + ";\n")

    print()
    print(sql)
