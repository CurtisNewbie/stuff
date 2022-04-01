import sys
import getopt

#
# Argument keys that only accept one single parameter
#
AUTHOR_ARG = "author"
PATH_ARG = "path"
EXCLUDE_ARG = "exclude"

#
# Flags that indicate a feature or a switch is turned on when they present 
#
MYBATISPLUS_FLAG = "mybatis-plus"
COPY_FLAG = "copy"
LAMBOK_FLAG = "lambok"
HELP_FLAG = 'help'

#
# some of the keywords (lowercase) that we care, may not contain all of them
#
keywords = {'unsigned'}
sql_types = {"varchar", "int", "tinyint", "short", "decimal", "datetime", "timestamp", "bigint", "char"}

CREATE = "create"
COMMENT = "comment"
COMMENT_EQUAL = COMMENT + "="
CONSTRAINT = "constraint"

# read file's content, and split it as lines
def read_file(filename): 
    f = open(filename, "r")
    lines = f.read().splitlines()
    f.close()
    return lines

# print help
def print_help():
    print("\n  sql_entity_gen by yongj.zhuang\n")
    print("  Help:\n")
    print(f"   Arguments:\n")
    print(f"    '{PATH_ARG} $path' : Path to the SQL DDL file")
    print(f"    '{AUTHOR_ARG} $author' : Author of the class")
    print(f"    '{EXCLUDE_ARG} $excludedField' : name of field to be excluded, this argument is repeatable")
    print(f"    '{MYBATISPLUS_FLAG}' : Enable mybatis-plus feature, e.g., @TableField, @TableName, etc")
    print(f"    '{COPY_FLAG}' : Enable copy to clipboard feature")
    print(f"    '{LAMBOK_FLAG}' : Enable lambok feature, e.g., @Data on class\n")
    print("  For example:\n")
    print(f"    python3 sql_entity_gen.py {PATH_ARG} book.sql {EXCLUDE_ARG} create_time {EXCLUDE_ARG} create_by {COPY_FLAG} {MYBATISPLUS_FLAG} {LAMBOK_FLAG}\n")
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

# prep array of ops and args for getopt
def prep_opt_arr():
    return [HELP_FLAG, MYBATISPLUS_FLAG, COPY_FLAG, LAMBOK_FLAG, PATH_ARG + '=', AUTHOR_ARG + '=', EXCLUDE_ARG+ '=']

def concat_flag(flag):
    return "--" + flag

if __name__ == '__main__':
    optlist, args = getopt.getopt(sys.argv[1:], '', prep_opt_arr()) 
    # print(f"optlist: {optlist}")
    # print(f"args: {args}")
    for tup in optlist:
        if tup[0] == concat_flag(HELP_FLAG):
            print_help()


