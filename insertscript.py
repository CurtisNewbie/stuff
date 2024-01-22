import argparse
import mysql.connector
import mysql.connector.cursor
import sys


def parsearg():
  ap = argparse.ArgumentParser("insertscript.py by Yongj.Zhuang")
  required = ap.add_argument_group('required arguments')
  required.add_argument("-user", '-u', help="username", type=str, required=True)
  ap.add_argument("-password", '-p', help="password (by default it's empty string)", type=str, default="", required=False)
  ap.add_argument("-host", help="host (by default it's localhost)", type=str, default="localhost", required=False)
  ap.add_argument("-table",  help="table", type=str, required=False, default="")
  return ap.parse_args()


"""
python3 -m pip install mysql-connector-python
"""
if __name__ == '__main__':
  args = parsearg()
  config = {
    'user': args.user,
    'password': args.password,
    'host': args.host,
    'database': None,
    'raise_on_warnings': True,
    'connect_timeout': 5000
  }

  cnx: mysql.connector.MySQLConnection = mysql.connector.connect(**config)
  cursor: mysql.connector.cursor.MySQLCursor = cnx.cursor()

  cursor.execute(f"select * from {args.table} limit 1")
  trs: list = cursor.fetchall()

  # print(f">> {args.table}")
  print()
  params = []
  columns = []


  script = []
  wrapped_cols = []
  cols = []
  for c in cursor.column_names:
    if c == 'id': continue
    cols.append(c)

  for c in cols:
    wrapped_cols.append('\"' + c + '\"')

  insert_start = f"INSERT INTO {args.table} \\n  ("
  for i in range(len(cols)):
    c = cols[i]
    insert_start = insert_start + c
    if i < len(cols) - 1:
      insert_start = insert_start + ","
  insert_start = insert_start + ") \\n  VALUES"

  script.append(f"columns = [ " + ','.join(wrapped_cols) + ' ]')

  param = '{'
  for i in range(len(cols)):
    c = cols[i]
    v = ''
    if c in ['created_at', 'updated_at']: v = 'CURRENT_TIMESTAMP'
    elif c == 'del_flag': v = 'N'

    param += f' \"{c}\" : \"{v}\"'
    if i < len(cols) - 1:
      param = param + ","
  param += ' }'

  script.append(f"""params = [
  {param},
]
""")

  script.append(f"print('{insert_start}')")
  script.append("")
  script.append("""for i in range(len(params)):
  p = params[i]
  qr = []
  for c in columns:
    qr.append(f'\"{p[c]}\"')

  o = '    (' + ','.join(qr) + ')'
  if i < len(params) -1 : o += ','
  print(o)
""")

  # print("\n".join(script))

  with open(f'insert_{args.table}.py', 'x') as f:
      f.write("\n".join(script))

  cursor.close()
  cnx.close()
