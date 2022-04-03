import sys

#
# Argument keys that only accept one single parameter
#
AUTHOR_ARG = "--author"
PATH_ARG = "--path"
EXCLUDE_ARG = "--exclude"


# set of arguments key
arg_set = (AUTHOR_ARG, PATH_ARG, EXCLUDE_ARG)

#
# Flags that indicate a feature or a switch is turned on when they present 
#
MYBATIS_PLUS_FLAG = "--mybatis-plus"
LAMBOK_FLAG = "--lambok"
HELP_FLAG = '--help'

# set of flag key (flag doesn't need value, it's just a flag)
flag_set  = (MYBATIS_PLUS_FLAG, LAMBOK_FLAG, HELP_FLAG)

#
# some constants
#
CREATE = "create"
TABLE = 'table'


# some of the keywords (lowercase) that we care, may not contain all of them
keywords = {'unsigned'}
# sql data types
sql_types = {"varchar", "int", "tinyint", "short", "decimal", "datetime", "timestamp", "bigint", "char"}

# sql type -> java type mapping (dict)
sql_java_type_mapping = {
    'varchar': 'String', 
    'datetime': 'LocalDateTime',
    'timestamp': 'LocalDateTime',
    'int' : 'Integer',
    'tinyint' : 'Integer',
    'short' : 'Integer',
    'bigint' : 'Long',
    'decimal' : 'BigDecimal',
    'char' : 'String'
}

# -----------------------------------------------------------
#
# global variables end here
#
# -----------------------------------------------------------


def write_file(path, content): 
    '''
    Write all content to a file

    arg[0] - file path

    arg[1] - content
    '''
    f = open(path, "w")
    lines = f.write(content)
    f.close()
    return lines


def read_file(path): 
    '''
    Read all content of a file in forms of a list of string, each represents a single line

    arg[0] - file path
    '''
    f = open(path, "r")
    lines = f.read().splitlines()
    f.close()
    return lines


def print_help():
    '''
    Print help
    '''
    print("\n  sql_entity_gen.py by yongj.zhuang\n")
    print("  Help:\n")
    print(f"   Arguments:\n")
    print(f"    '{PATH_ARG} $path' : Path to the SQL DDL file")
    print(f"    '{AUTHOR_ARG} $author' : Author of the class")
    print(f"    '{EXCLUDE_ARG} $excludedField' : name of field to be excluded, this argument is repeatable")
    print(f"    '{MYBATIS_PLUS_FLAG}' : Enable mybatis-plus feature, e.g., @TableField, @TableName, etc")
    print(f"    '{LAMBOK_FLAG}' : Enable lambok feature, e.g., @Data on class\n")
    print("  For example:\n")
    print(f"    python3 sql_entity_gen.py {PATH_ARG} book.sql {EXCLUDE_ARG} create_time {EXCLUDE_ARG} create_by {MYBATIS_PLUS_FLAG} {LAMBOK_FLAG}\n")
    print("  This tool parse a SQL DDL script file, and then generate a ")
    print("  simple Java Class for this 'table'. The SQL file should ")
    print("  only contain one 'CREATE TABLE' statement.\n")
    print("  Each line should only contain key words for a single field,")
    print("  so don't put everything in one line.\n")
    print("  For example:\n")
    print("  CREATE TABLE IF NOT EXISTS book (")
    print("    id INT UNSIGNED PRIMARY KEY AUTO_INCREMENT COMMENT \"primary key\",")
    print("    name VARCHAR(255) NOT NULL DEFAULT '' COMMENT 'name of the book',")
    print("    create_time DATETIME NOT NULL DEFAULT NOW() COMMENT 'when the record is created',")
    print("    create_by VARCHAR(255) NOT NULL DEFAULT '' COMMENT 'who created this record',")
    print("    update_time DATETIME NOT NULL DEFAULT NOW() COMMENT 'when the record is updated',")
    print("    update_by VARCHAR(255) NOT NULL DEFAULT '' COMMENT 'who updated this record',")
    print("    is_del TINYINT NOT NULL DEFAULT '0' COMMENT '0-normal, 1-deleted'")
    print(" ) ENGINE=InnoDB COMMENT 'Some nice books'\n\n")


def concat_flag(flag):
    return "--" + flag


def is_flag(key):
    '''whether the key is flag '''
    return key in flag_set


def is_arg(key):
    '''Whether the key is an argument (key-value)'''
    return key in arg_set


class Context:  
    '''Context'''

    def __init__(self, argv): 
        # key: string, value: list of string
        self.ctx_dict = {}
        self._parse_context(argv) 

    def _put(self, k, v):
        '''
        put key -> value in context, value is not overwritten when key collides

        arg[0] - key, arg[1] - value
        '''
        if k in self.ctx_dict:
            self.ctx_dict[k].append(v)
        else:
            self.ctx_dict[k] = [v]

    def _parse_context(self, argv):
        '''
        Parse arguments

        arg[0] - list of string
        '''
        i = 0
        l = len(argv)
        if l == 0:
            print("Error - Argument list is empty")
            sys.exit(1)

        while i < l:
            ar = argv[i]
            if is_flag(ar):
                self._put(ar, '')
                i+=1
            else:
                if i + 1 > l:
                    print(f"Error - {ar}'s argument is missing")
                    sys.exit(1)
                self._put(ar, argv[i+1])
                i+=2

    def is_present(self, k):
        '''
        Whether key is present

        arg[0] - key
        '''
        return k in self.ctx_dict

    def get_first(self, k):
        '''
        Get first value for given key

        arg[0] - key
        '''
        return self.get(k)[0]

    def get(self, k):
        '''
        Get values for given key, a list is returned

        arg[0] - key
        '''
        return self.ctx_dict[k]

    def __str__(self):
        s = ''
        for k in self.ctx_dict:
            if s != '':
                s += '\n'
            s += f'key: "{k}" -> value: {self.ctx_dict[k]}'
        return s


def assert_true(flag, msg):  
    if flag is not True: 
       print(f"Error - {msg}") 
       sys.exit(1)

def parse_ddl(lines):
    '''
    Parse 'CREATE TABLE' DDL Script

    arg[0] - list of string, each represents a single line
    '''
    table_name = None
    table_comment = None
    fields = []
    l = len(lines)

    for i in range(l):
        trimmed = lines[i].strip()
        if trimmed == '':
            continue

        tokens = trimmed.split(" ")
        line_no = i+ 1;

        if strmatches(tokens[0], CREATE):
            assert_true(table_name == None, "CREATE keyword is already used, please check your syntax")
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
    

def strmatches(t, v):
    '''Check whether two string matches ignore cases'''
    return t.casefold() == v.casefold()

# data structures used by is_constraint() method
single_constraint_keywords = {'constraint', 'unique', 'index', 'key'}
comb_constraint_keywords = {'primary', 'foreign'}

def is_constraint(tokens):
    '''
    Check whether the line is for constraint specification

    arg[0] - list of string for a single line (i.e., a line that is tokenized)
    '''
    lt = tokens[0].lower()
    if lt in single_constraint_keywords:
        return True
    
    if lt in comb_constraint_keywords and strmatches(tokens[1], 'key'):
        return True

    return False


def parse_field(tokens, line_no):
    '''
    Parse field for the current line

    arg[0] - list of string for a single line (i.e., a line that is tokenized)

    arg[1] - current line number
    '''
    field_name = tokens[0]
    assert_true(field_name not in sql_types, f"Failed to parse DDL, field name {field_name} can't be a keyword, illegal syntax at line {line_no}")

    type = None
    kw = set()

    for i in range(1, len(tokens)):
        tk = tokens[i].lower()
        for t in sql_types:
            if type is None and tk.startswith(t):
                type = t

        if tk in keywords:
            kw.add(tk)

    assert_true(type is not None, f"Failed to parse DDL, unable to identify data type for field '{field_name}', illegal syntax at line {line_no}")
    return SQLField(field_name, kw, type, extract_comment(tokens, line_no))


def first_char_upper(str):
    '''Make first char uppercase'''
    return str[0:1].upper() + str[1:]


def generate_java_class(table, ctx):
    '''
    Generate Java class, and return it as a string

    arg[0] - SQLTable object
    
    arg[1] - Context object
    '''

    # features
    mbp_ft = ctx.is_present(MYBATIS_PLUS_FLAG)
    lambok_ft = ctx.is_present(LAMBOK_FLAG)

    table_camel_case =  to_camel_case(table.table_name)
    class_name = first_char_upper(table_camel_case)
    s = ''

    # always import util, time and math
    s += "import java.util.*;\n"
    s += "import java.time.*;\n"
    s += "import java.math.*;\n\n"

    # for mybatis-plus only
    if mbp_ft:
        s += "import com.baomidou.mybatisplus.annotation.IdType;\n"
        s += "import com.baomidou.mybatisplus.annotation.TableField;\n"
        s += "import com.baomidou.mybatisplus.annotation.TableId;\n"

    # for lambok
    if lambok_ft:
        s += "import lombok.*;\n"

    s += f'\n'
    s += f'/**\n'
    s += f" * {table.table_comment}\n"

    # author
    if ctx.is_present(AUTHOR_ARG):
        s += f' *\n'
        s += f' * @author {ctx.get_first(AUTHOR_ARG)}\n'

    s += f' */\n'

    if lambok_ft:
        s += '@Data\n'

    if mbp_ft:
        s += f"@TableName(value = \"{table.table_name}\")\n"

    s += f"public class {class_name} {{\n\n"

    excl = ctx.get(EXCLUDE_ARG) if ctx.is_present(EXCLUDE_ARG) else set()

    # fields
    for f in table.fields:
        if f.sql_field_name in excl: 
            continue

        s += f"    /** {f.comment} */\n"
        if mbp_ft: 
            if strmatches(f.sql_field_name, 'id'):
                s += "    @TableId(type = IdType.AUTO)\n"
            else:
                s += f"    @TableField(\"{f.sql_field_name}\")\n"
        s += f"    private {f.java_type} {f.java_field_name};\n\n"


    # getter setters
    if not lambok_ft:
        for f in table.fields:
            us = first_char_upper(f.java_field_name)
            s += f"    public {f.java_type} get{us}() {{\n"
            s += f"        return this.{f.java_field_name}\n"
            s += f"    }}\n\n"

            s += f"    public void set{us}({f.java_type} {f.java_field_name}) {{\n"
            s += f"        this.{f.java_field_name} = {f.java_field_name};\n"
            s += f"    }}\n\n"

    s += '}\n'
    return s

def extract_comment(tokens, line_no):
    '''
    Extract comment 

    arg[0] - list of string (tokens) for a single line

    arg[1] - current line no
    '''

    err_msg = f"Failed to parse DDL, multiple COMMENT keyword is found, illegal syntax at line: {line_no}" 

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
            assert_true(l == -1, err_msg)
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
                    assert_true(i < llen, f'Syntax error, unable to find the opening quote for comment at line: {line_no}')
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
    return joined[joined.find(quote): joined.rfind(quote) + 1]


def first_quote(s, after=-1):
    sq = s.find('\'', after)
    dq = s.find('\"', after)
    if sq == -1 and dq == -1:
        return [None, -1]
    if sq == -1:
        return ['\"', dq]
    elif dq == -1: 
        return ['\'', sq]

    return ['\'', sq] if sq < dq else ['\"', dq]

def extract_table_name(tokens, line_no):
    '''
    Extract table name

    arg[0] - list of string (tokens) for a single line

    arg[1] - current line no
    '''
    err_msg = f"Illegal CREATE TABLE statement at line: {line_no}"

    l = len(tokens)
    assert_true(l >= 4, err_msg)
    assert_true(l > 4 and l == 7, err_msg)
    assert_true(strmatches(tokens[0], CREATE), err_msg)
    assert_true(strmatches(tokens[1], TABLE), err_msg)

    name = ''
    if l == 4:
        name = tokens[2]
    else:
        assert_true(strmatches(tokens[2], "if"), err_msg)
        assert_true(strmatches(tokens[3], "not"), err_msg)
        assert_true(strmatches(tokens[4], "exists"), err_msg)
        name = tokens[5]

    name = name.replace("`", "")
    i = name.find('.')
    if i > -1:
        name = name[i + 1: len(name)]
    return name

def to_java_type(keywords, sql_type):
    '''
    Guess the Java data type for the given SQL type 

    arg[0] - set of keywords that may help the prediction

    arg[1] - SQL datatype
    '''

    sql_type = sql_type.lower()

    # special case for unsigned int
    if sql_type == 'int' and 'unsigned' in keywords:
        return 'Long'

    assert_true(sql_type in sql_java_type_mapping, f"Unable to find corresponding java type for {sql_type}")

    return sql_java_type_mapping[sql_type]

def to_camel_case(str):
    '''
    Convert a string to camel case
    '''
    prev_is_ul = False
    str = str.lower()
    ccs = ''
    for i in range(len(str)):
        ci = str[i]
        if ci == '_':
            prev_is_ul = True
        else:
            if prev_is_ul:
                ccs += ci.upper()
                prev_is_ul = False
            else:
                ccs += ci
    return ccs


class SQLField:
    '''
    SQL Field
    '''

    def __init__(self, field_name, keywords, sql_type, comment):
        self.sql_field_name = field_name.replace('`', '')
        self.keywords = keywords
        self.sql_type = sql_type
        self.comment = comment
        self.java_type = to_java_type(keywords, sql_type)
        self.java_field_name = to_camel_case(self.sql_field_name)


    def __str__(self):
        return f"Field: {self.sql_field_name} ({self.java_field_name}), type: {self.sql_type} ({self.java_type}), comment: \'{self.comment}\'"


class SQLTable:
    '''
    SQL Table with fields in it
    '''

    def __init__(self, table_name, table_comment, fields):
        self.table_name = table_name
        self.table_comment = '' if table_comment is None else table_comment
        self.fields = fields

    def __str__(self):
        s = '' 
        s += f"Table: {self.table_name}\n"
        s += f"Comment: {self.table_comment}\n"
        for f in self.fields:
            s+= f" - {f}\n"
        return s

# -----------------------------------------------------------
#
# Main 
#
# -----------------------------------------------------------

if __name__ == '__main__':
    args = sys.argv[1:]

    # parse args as context
    ctx = Context(args)
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
    fname = first_char_upper(to_camel_case(table.table_name)) + ".java"
    write_file(fname, generated)
    print(f"Java class generated and written to \'{fname}\'")
