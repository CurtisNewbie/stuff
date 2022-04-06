from util import *

#
# Argument keys that only accept one single parameter
#
AUTHOR_ARG: str = "--author"
PATH_ARG: str = "--path"
EXCLUDE_ARG: str = "--exclude"
OUTPUT_ARG: str = "--output"

#
# Flags that indicate a feature or a switch is turned on when they present 
#
MYBATIS_PLUS_FLAG: str = "--mybatis-plus"
LAMBOK_FLAG: str = "--lambok"
HELP_FLAG: str = '--help'

# set of flag key (flag doesn't need value, it's just a flag)
flag_set: Set[str] = {MYBATIS_PLUS_FLAG, LAMBOK_FLAG, HELP_FLAG}

#
# some constants
#
CREATE: str = "create"
TABLE: str = "table"

# some keywords (lowercase) that we care, may not contain all of them
sql_keywords = {'unsigned'}
# sql data types
sql_types = {"varchar", "int", "tinyint", "short", "decimal", "datetime", "timestamp", "bigint", "char"}

# sql type -> java type mapping (dict)
sql_java_type_mapping = {
    'varchar': 'String',
    'datetime': 'LocalDateTime',
    'timestamp': 'LocalDateTime',
    'int': 'Integer',
    'tinyint': 'Integer',
    'short': 'Integer',
    'bigint': 'Long',
    'decimal': 'BigDecimal',
    'char': 'String'
}


# -----------------------------------------------------------
#
# global variables end here
#
# -----------------------------------------------------------

def arr_partial_matches(arr: List[str], param: List[str], start: int = 0) -> bool:
    """
    Partial Matching between two array

    arg[0] - list of string that is validated
    arg[1] - list of string as parameters that validate the arg[0]
    arg[2] - starting index for arg[0] (default 0)
    """
    al = len(arr)
    for i, p in enumerate(param, start):
        if i > al:
            return False
        if not str_matches(arr[i], p):
            return False
    return True


def is_not_comment(line: str) -> bool:
    """Return true if it's not a comment else false"""
    return False if line.strip().startswith("--") else True


def print_help():
    """
    Print help
    """
    print("\n  sql_entity_gen.py by yongj.zhuang\n")
    print("  Help:\n")
    print("  Arguments:\n")
    print(f"{T}'{PATH_ARG} $path' : Path to the SQL DDL file")
    print(f"{T}'{AUTHOR_ARG} $author' : Author of the class")
    print(f"{T}'{EXCLUDE_ARG} $field' : one or move field to be excluded (delimited by \',\')")
    print(f"{T}'{MYBATIS_PLUS_FLAG}' : Enable mybatis-plus feature, e.g., @TableField, @TableName, etc")
    print(f"{T}'{OUTPUT_ARG}' : (Optional) Where the generate java class is written to")
    print(f"{T}'{LAMBOK_FLAG}' : Enable lambok feature, e.g., @Data on class\n")
    print("  For example:\n")
    print(
        f"{T}python3 sql_entity_gen.py {PATH_ARG} book.sql {EXCLUDE_ARG} \'create_time,create_by\' {MYBATIS_PLUS_FLAG} {LAMBOK_FLAG} {OUTPUT_ARG} Book.java\n")
    print(f"{T}This tool parse a SQL DDL script file, and then generate a ")
    print(f"{T}simple Java Class for this 'table'. The SQL file should ")
    print(f"{T}only contain one 'CREATE TABLE' statement.\n")
    print(f"{T}Each line should only contain key words for a single field,")
    print(f"{T}so don't put everything in one line.\n\n")
    print("  About Data Type Mapping:\n")
    print(data_type_mapping_str(T))
    print("  For example:\n")
    print(f"{T}CREATE TABLE IF NOT EXISTS book (")
    print(f"{TT}id INT UNSIGNED PRIMARY KEY AUTO_INCREMENT COMMENT \"primary key\",")
    print(f"{TT}name VARCHAR(255) NOT NULL DEFAULT '' COMMENT 'name of the book',")
    print(f"{TT}create_time DATETIME NOT NULL DEFAULT NOW() COMMENT 'when the record is created',")
    print(f"{TT}create_by VARCHAR(255) NOT NULL DEFAULT '' COMMENT 'who created this record',")
    print(f"{TT}update_time DATETIME NOT NULL DEFAULT NOW() COMMENT 'when the record is updated',")
    print(f"{TT}update_by VARCHAR(255) NOT NULL DEFAULT '' COMMENT 'who updated this record',")
    print(f"{TT}is_del TINYINT NOT NULL DEFAULT '0' COMMENT '0-normal, 1-deleted'")
    print(f"{T}) ENGINE=InnoDB COMMENT 'Some nice books'\n\n")


def data_type_mapping_str(pre: str) -> str:
    """
    Concat data type mapping as string
    """
    s = ''
    for k in sql_java_type_mapping:
        s += f"{pre}{k} -> {sql_java_type_mapping[k]}\n"
    return s


def parse_ddl(lines: List[str]):
    lines = list(filter(is_not_comment, lines))

    """
    Parse 'CREATE TABLE' DDL Script

    arg[0] - list of string, each represents a single line
    """
    table_name = None
    table_comment = None
    fields = []
    l = len(lines)

    for i in range(l):
        trimmed = lines[i].strip()
        if trimmed == '':
            continue

        tokens = trimmed.split(" ")
        line_no = i + 1

        if str_matches(tokens[0], CREATE):
            assert_true(table_name is None, "CREATE keyword is already used, please check your syntax")
            table_name = extract_table_name(tokens, line_no)
        elif tokens[0].startswith(')'):
            table_comment = extract_comment(tokens, line_no)
        else:
            if is_constraint(tokens):
                continue
            fields.append(parse_field(tokens, line_no))

    assert_true(table_name is not None, 'Failed to parse DDL, table name is not found')
    assert_true(len(fields) > 0, 'Failed to parse DDL, this table doesn\'t have fields')

    return SQLTable(table_name, table_comment, fields)


# data structures used by is_constraint() method
single_constraint_keywords: Set[str] = {'constraint', 'unique', 'index', 'key'}
comb_constraint_keywords: Set[str] = {'primary', 'foreign'}


def is_constraint(tokens: List[str]) -> bool:
    """
    Check whether the line is for constraint specification

    arg[0] - list of string for a single line (i.e., a line that is tokenized)
    """
    lt = tokens[0].lower()
    if lt in single_constraint_keywords:
        return True

    if lt in comb_constraint_keywords and str_matches(tokens[1], 'key'):
        return True

    return False


def parse_field(tokens: list, line_no: int) -> "SQLField":
    """
    Parse field for the current line

    arg[0] - list of string for a single line (i.e., a line that is tokenized)

    arg[1] - current line number
    """
    field_name: str = tokens[0]
    assert_true(field_name not in sql_types,
                f"Failed to parse DDL, field name {field_name} can't be a keyword, illegal syntax at line {line_no}")

    st: str = None
    kw: Set[str] = set()

    for i in range(1, len(tokens)):
        tk = tokens[i].lower()
        for t in sql_types:
            if st is None and tk.startswith(t):
                st = t

        if tk in sql_keywords:
            kw.add(tk)

    assert_true(st is not None,
                f"Failed to parse DDL, unable to identify data type for field '{field_name}', illegal syntax at line {line_no}")
    return SQLField(field_name, kw, st, extract_comment(tokens, line_no))


def generate_java_class(table: "SQLTable", ctx: "Context") -> str:
    """
    Generate Java class, and return it as a string

    arg[0] - SQLTable object

    arg[1] - Context object
    """

    # features
    mbp_ft = ctx.is_present(MYBATIS_PLUS_FLAG)
    lambok_ft = ctx.is_present(LAMBOK_FLAG)

    table_camel_case = to_camel_case(table.table_name)
    class_name = first_char_upper(table_camel_case)
    s = ''

    '''
        For Imports 
    '''
    s += "import java.util.*;\n"
    if table.is_type_used('LocalDateTime'):
        s += "import java.time.*;\n"
    if table.is_type_used('BigDecimal'):
        s += "import java.math.*;\n"
    s += '\n'

    # for mybatis-plus only
    if mbp_ft:
        s += "import com.baomidou.mybatisplus.annotation.IdType;\n"
        s += "import com.baomidou.mybatisplus.annotation.TableField;\n"
        s += "import com.baomidou.mybatisplus.annotation.TableId;\n"
    s += '\n'

    # for lambok
    if lambok_ft:
        s += "import lombok.*;\n"

    s += '\n'
    s += '/**\n'
    s += f" * {table.table_comment}\n"

    # author
    if ctx.is_present(AUTHOR_ARG):
        s += ' *\n'
        s += f' * @author {ctx.get_first(AUTHOR_ARG)}\n'

    s += ' */\n'

    if lambok_ft:
        s += '@Data\n'

    if mbp_ft:
        s += f"@TableName(value = \"{table.table_name}\")\n"

    s += f"public class {class_name} {{\n\n"

    '''
        Fields
    '''
    excluded = set()
    if ctx.is_present(EXCLUDE_ARG):
        for x in ctx.get(EXCLUDE_ARG):
            for v in list(filter(is_not_empty_str, x.split(','))):
                excluded.add(v.strip())

    for f in table.fields:
        if f.sql_field_name in excluded:
            continue

        s += f"{T}/** {f.comment} */\n"
        if mbp_ft:
            if str_matches(f.sql_field_name, 'id'):
                s += f"{T}@TableId(type = IdType.AUTO)\n"
            else:
                s += f"{T}@TableField(\"{f.sql_field_name}\")\n"
        s += f"{T}private {f.java_type} {f.java_field_name};\n\n"

    ''' 
        Getter, setters only appended when lambok is not used
    '''
    if not lambok_ft:
        for f in table.fields:
            us = first_char_upper(f.java_field_name)
            s += f"{T}public {f.java_type} get{us}() {{\n"
            s += f"{TT}return this.{f.java_field_name}\n"
            s += f"{T}}}\n\n"

            s += f"{T}public void set{us}({f.java_type} {f.java_field_name}) {{\n"
            s += f"{TT}this.{f.java_field_name} = {f.java_field_name};\n"
            s += f"{T}}}\n\n"

    s += '}\n'
    return s


def extract_comment(tokens, line_no) -> str:
    """
    Extract comment

    arg[0] - list of string (tokens) for a single line

    arg[1] - current line no
    """

    llen = len(tokens)
    l = -1
    h = -1
    quote = '\''

    # try to find comment, it won't be the first one anyway
    i = 0
    while i < llen:

        # COMMENT = 'xxx  or COMMENT =' xxx  or COMMENT= 'xxx  or COMMENT=' xxx 
        if tokens[i].lower().startswith('comment'):

            # make sure there is only one COMMENT keyword
            assert_true(l == -1,
                        f"Failed to parse DDL, multiple COMMENT keyword is found, illegal syntax at line: {line_no}")
            l = i

            # find where the equal sign is 
            # if no equal sign found
            # then it's the COMMENT = ..... case
            eq = tokens[i].find('=')
            if eq == -1:
                l = i + 1
            else:
                # found equal sign
                # it may be COMMENT='xxx or COMMENT= 'xxx
                # try to find the quotes
                # maybe there is a ' or " after the eq sign ?
                qt = first_quote(tokens[i], eq - 1)

                # no quote is found, we must find one, if we don't, this is a syntax error
                if qt[0] is None:
                    while i < llen:
                        qt = first_quote(tokens[i])
                        if qt[0] is not None:
                            quote = qt[0]
                            l = i
                            break
                        i += 1

                    # opening quote is not found, syntax error
                    assert_true(i < llen,
                                f'Syntax error, unable to find the opening quote for comment at line: {line_no}')
                else:
                    # which quote is used (' or ")
                    quote = qt[0]
                    l = i

                # current token is also the end of the comment
                # which is the case: COMMENT='xxx'
                if tokens[i].rfind(quote) > qt[1]:
                    h = i
                    break
        else:
            # the opening quote is already found, try to find the ending quote
            if l > -1 and tokens[i].rfind(quote) > 0:
                h = i
                break
        i += 1

    # no comment found
    if l == -1 or h == -1:
        return ''

    joined = ' '.join(tokens[l: h + 1])
    return joined[joined.find(quote) + 1: joined.rfind(quote)]


def first_quote(s, after=-1) -> List[str]:
    """
    Find the first quote being used, it may be a single  quote or a double quote

    arg[0] - string to be searched
    arg[1] - starting index (default is -1)

    return - a list, where [0] is the quote being used or None, and [1] is the left first index of the quote
    """
    sq = s.find('\'', after)
    dq = s.find('\"', after)
    if sq == -1 and dq == -1:
        return [None, -1]
    if sq == -1:
        return ['\"', dq]
    elif dq == -1:
        return ['\'', sq]

    return ['\'', sq] if sq < dq else ['\"', dq]


def extract_table_name(tokens: List[str], line_no: int) -> str:
    """
    Extract table name

    arg[0] - list of string (tokens) for a single line

    arg[1] - current line no
    """
    tokens = list(filter(is_not_empty_str, tokens))
    err_msg = f"Illegal CREATE TABLE statement at line: {line_no}"
    tlen = len(tokens)

    assert_true(tlen >= 4, err_msg, 'Invalid number to tokens, must be greater or equal to 4')
    if tlen > 4:
        assert_true(tlen == 7, err_msg)
    assert_true(arr_partial_matches(tokens, [CREATE, TABLE]), err_msg, 'Does not matches CREATE TABLE ...')

    if tlen == 4:  # create table [table_name]
        name = tokens[2]
    else:  # create table if not exists [table_name]
        assert_true(arr_partial_matches(tokens, ['if', 'not', 'exists'], 2), err_msg,
                    'Does not matches CREATE TABLE IF NOT EXISTS')
        name = tokens[5]

    name = name.replace("`", "")
    i = name.find('.')
    if i > -1:
        name = name[i + 1: len(name)]
    return name


def to_java_type(keywords: Set[str], sql_type: str) -> str:
    """
    Guess the Java data type for the given SQL type

    arg[0] - set of keywords that may help the prediction

    arg[1] - SQL datatype
    """

    sql_type = sql_type.lower()

    # special case for unsigned int
    if sql_type == 'int' and 'unsigned' in keywords:
        return 'Long'

    assert_true(sql_type in sql_java_type_mapping, f"Unable to find corresponding java type for {sql_type}")

    return sql_java_type_mapping[sql_type]


class SQLField:
    """
    SQL Field
    """

    def __init__(self, field_name: str, keywords: set, sql_type: str, comment: str):
        self.sql_field_name = field_name.replace('`', '')
        self.keywords = keywords
        self.sql_type = sql_type
        self.comment = comment
        self.java_type = to_java_type(keywords, sql_type)
        self.java_field_name = to_camel_case(self.sql_field_name)

    def __str__(self):
        return f"Field: {self.sql_field_name} ({self.java_field_name}), type: {self.sql_type} ({self.java_type}), " \
               f"comment: \'{self.comment}\' "


class SQLTable:
    """
    SQL Table with fields in it
    """

    def __init__(self, table_name: str, table_comment: str, fields: List["SQLField"]):
        self.table_name = table_name
        self.table_comment = '' if table_comment is None else table_comment
        self.fields = fields
        self.java_type_set = set()
        for f in fields:
            self.java_type_set.add(f.java_type)

    def __str__(self):
        s = ''
        s += f"Table: {self.table_name}\n"
        s += f"Comment: {self.table_comment}\n"
        for f in self.fields:
            s += f" - {f}\n"
        return s

    def is_type_used(self, java_type: str):
        """
        Check whether the java type is used in this table

        arg[0] - java type name
        """
        return java_type in self.java_type_set


""" 
SQL to Java Entity Generator  

yongj.zhuang
"""

if __name__ == '__main__':
    args = sys.argv[1:]

    # no arg provided
    if len(args) == 0:
        print_help()
        sys.exit(0)

    # parse args as context
    ctx = Context(args, lambda x: x in flag_set)
    if ctx.is_present(HELP_FLAG):
        print_help()
        sys.exit(0)

    # read file
    assert_true(ctx.is_present(PATH_ARG), f'Argument for "{PATH_ARG}" is not found')
    path = ctx.get_first(PATH_ARG)
    lines = read_file(path)

    # parse ddl
    table = parse_ddl(lines)
    print(table)

    # generate java class                                       
    generated = generate_java_class(table, ctx)

    # write to file
    if ctx.is_present(OUTPUT_ARG):
        fn = ctx.get_first(OUTPUT_ARG)
    else:
        fn = first_char_upper(to_camel_case(table.table_name)) + ".java"
    write_file(fn, generated)
    print(f"Java class generated and written to \'{fn}\'")
