from genericpath import exists
import sys
from typing import Callable
import pandas

isdebug = False


def debug(callback: Callable[[], str]):
    '''
    print debug log, only if 'isdebug' = True
    '''
    if isdebug:
        print("[debug] " + callback())


class ExcelParser():

    def __init__(self, inputf) -> None:
        self.inputf = inputf
        self.cols: list[str] = None
        self.rows: list[list[str]] = None

    def parse(self):
        ip = self.inputf
        if ip == None:
            raise ValueError("Please specify input file")
        debug(lambda: f"input path: '{ip}'")

        # read and parse workbook
        if not exists(ip):
            raise ValueError(f"Input file '{ip}' not found")

        df: pandas.DataFrame = pandas.read_excel(ip, 0, dtype="string")
        # debug(lambda: f"opened workbook '{ip}', content: '{df}'")

        nrow = len(df)
        ncol = len(df.columns)
        debug(lambda: f"row count: {nrow}, col count: {ncol}")

        # columns
        cols = []
        for i in range(ncol):
            h = df.columns[i]
            if not h:
                break
            cols.append(str(h))

        if isdebug:
            s = "Columns: "
            for i in range(len(cols)):
                s += f"[{i}] {cols[i]}"
                if i < len(cols) - 1:
                    s += ", "
            debug(lambda: s)

        # rows
        rows: list[list[str]] = []
        for i in range(nrow):
            r = []
            for j in range(ncol):
                v = df.iat[i, j]
                if pandas.isnull(v):
                    v = ""
                r.append(v)

            rows.append(r)
            debug(lambda: f"row[{i}]: {r}")

        self.cols = cols
        self.rows = rows


'''
python3 -m pip install pandas openpyxl 

(openpyxl is optional, it's used for *.xlsx files)

[0] - input path

'--debug' for debug mode

Yongj.Zhuang
'''
if __name__ == '__main__':

    la = len(sys.argv)
    if la < 2:
        print("\n excelparser.py (pandas) by Yongj.Zhuang")
        print("\n Please provide following arguments:\n")
        print(" [0] - input path")
        print("\n e.g., python3 excelparser.py myexcel.xls")
        print("\n '--debug' for debug mode")
        sys.exit(1)

    ip = None
    for i in range(1, la):
        v = sys.argv[i]
        if v == "--debug":
            isdebug = True
        else:
            ip = v

    ep = ExcelParser(ip)
    ep.parse()
