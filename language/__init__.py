from language import struct_tokenizer
from language import struct_parser
from language import struct_compiler

def parse_file(path):
    with open(path, "r") as f:
        src = f.read()
    tokens = struct_tokenizer.tokenize_structure(src)
    ast = struct_parser.parse_structure(tokens)
    res = struct_compiler.compile_structure(ast)
    return res