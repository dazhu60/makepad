#!/usr/bin/python3

import argparse

# The largest valid Unicode code point
MAX_CODE_POINT = 0x10FFFF

class Error(Exception):
    """Error base class."""

def parse_code_point(string):
    """Parses a Unicode code point.

    Code points are expressed as hexadecimal numbers with four to six digits.
    """
    if len(string) < 4 or len(string) > 6:
        raise Error("invalid code point %s" % string)
    try:
        code_point = int(string, 16)
    except ValueError:
        raise Error("invalid code point %s" % string)
    if code_point < 0 or code_point > MAX_CODE_POINT:
        raise Error("invalid code point %s" % string)
    return code_point

def parse_test(string):
    substrings = []
    substring = ""
    for code_point in string.split():
        if code_point == '×':
            continue
        if code_point == '÷':
            if len(substring) > 0:
                substrings.append(substring)
            substring = ""
            continue
        substring += chr(parse_code_point(code_point))
    if len(substring) > 0:
        substrings.append(substring)
    return substrings

def load_test_data(filename):
    tests = []
    file = open(filename, encoding="utf8")
    lineno = 1
    for line in file:
        hash = line.find("#")
        if hash >= 0:
            line = line[:hash]
        line = line.strip()
        if not line:
            continue
        try:
            tests.append(parse_test(line))
        except Exception as e:
            e.args = ("%s:%d:" % (filename, lineno), *e.args)
            raise e.with_traceback(e.__traceback__)   
        lineno += 1
    return tests

def format_string_literal(string):
    out = "\""
    for char in string:
        out += "\\u{%X}" % ord(char)
    out += "\""
    return out

def format_test(test):
    out = "&["
    first = True
    for string in test:
        if not first:
            out += ", "
        out += format_string_literal(string)
        first = False
    out += "]"
    return out

def print_test_data(name, tests):
    print("//! This file was generated by:")
    print("//! generate_test_data.py %s <ucd_dir>" % name)
    print("")
    print("pub static TEST_DATA: [&'static [&'static str]; %d] = [" % len(tests))
    for test in tests:
        print("    %s," % format_test(test))
    print("];")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("name", type=str)
    parser.add_argument("ucd_dir", type=str)
    args = parser.parse_args()
    if args.name == "grapheme":
        print_test_data(args.name, load_test_data(args.ucd_dir + "/auxiliary/GraphemeBreakTest.txt"))
    elif args.name == "word":
        print_test_data(args.name, load_test_data(args.ucd_dir + "/auxiliary/WordBreakTest.txt"))
    else:
        raise Error("invalid segment name")

if __name__ == '__main__':
    main()