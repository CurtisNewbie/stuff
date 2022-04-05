import sys
from typing import List, Dict, Set


def first_char_upper(s: str) -> str:
    """Make first char uppercase"""
    return s[0:1].upper() + s[1:]


def str_matches(t: str, v: str) -> bool:
    """Check whether two string matches ignore cases"""
    return t.casefold() == v.casefold()


def read_file(path: str) -> List[str]:
    """
    Read all content of a file in forms of a list of string, each represents a single line

    arg[0] - file path
    """
    f = open(path, "r")
    lines = f.read().splitlines()
    f.close()
    return lines


def write_file(path: str, content: str) -> None:
    """
    Write all content to a file

    arg[0] - file path

    arg[1] - content
    """
    f = open(path, "w")
    f.write(content)
    f.close()


def to_camel_case(s: str) -> str:
    """
    Convert a string to camel case
    """
    is_prev_uc = False  # is prev in uppercase
    s = s.lower()
    ccs = ''
    for i in range(len(s)):
        ci = s[i]
        if ci == '_':
            is_prev_uc = True
        else:
            if is_prev_uc:
                ccs += ci.upper()
                is_prev_uc = False
            else:
                ccs += ci
    return ccs


def is_not_empty_str(s: str) -> bool:
    """Return true if string is not empty else false"""
    return False if s.strip() == '' else True


def assert_true(flag: bool, msg: str, hint: str = None) -> None:
    """Assert the given flag is true, else print an error msg and exit the program"""
    if flag is not True:
        s = f"[Error] {msg}"
        if hint is not None:
            s += f" hint: {hint}"
        print(s)
        sys.exit(1)


class Context:
    """Context"""

    def __init__(self, argv: List[str], is_flag_predicate_func):
        """
        Create a new Context by parsing the given arguments list

        :param argv: list of str
        :param is_flag_predicate_func: function that takes a str and returns bool indicating whether the given str is a
            flag or not
        """
        self.ctx_dict: Dict[str, List[str]] = {}
        self.is_flag_predicate_func = is_flag_predicate_func
        self._parse_context(argv)

    def _put(self, k: str, v: str):
        """
        put key -> value in context, value is not overwritten when key collides

        arg[0] - key, arg[1] - value
        """
        if k in self.ctx_dict:
            self.ctx_dict[k].append(v)
        else:
            self.ctx_dict[k] = [v]

    def _parse_context(self, argv: List[str]):
        """
        Parse arguments

        arg[0] - list of string
        """
        argv = list(filter(is_not_empty_str, argv))

        i = 0
        al = len(argv)
        if al == 0:
            print("Error - Argument list is empty")
            sys.exit(1)

        while i < al:
            ar = argv[i]
            if self.is_flag_predicate_func(ar):
                self._put(ar, '')
                i += 1
            else:
                if i + 1 > al:
                    print(f"Error - {ar}'s argument is missing")
                    sys.exit(1)
                self._put(ar, argv[i + 1])
                i += 2

    def is_present(self, k: str) -> bool:
        """
        Whether key is present

        arg[0] - key
        """
        return k in self.ctx_dict

    def get_first(self, k: str) -> str:
        """
        Get first value for given key

        arg[0] - key
        """
        return self.get(k)[0]

    def get(self, k: str) -> List[str]:
        """
        Get values for given key, a list is returned

        arg[0] - key
        """
        return self.ctx_dict[k]

    def __str__(self):
        s = ''
        for k in self.ctx_dict:
            if s != '':
                s += '\n'
            s += f'key: "{k}" -> value: {self.ctx_dict[k]}'
        return s
