from language import struct_tokenizer
from language import struct_parser
from language import struct_compiler
from language.parser_error import ParserError
import sys

def parse_file(path):
    with open(path, "r") as f:
        src = f.read()
    try:
        tokens = struct_tokenizer.tokenize_structure(src)
        ast = struct_parser.parse_structure(tokens)
        res = struct_compiler.compile_structure(ast)
    except ParserError as e:
        print(f"error reading {path}:")
        print(e.error_message)
        sys.exit(1)
    return res