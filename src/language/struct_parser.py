from language.parser_error import ParserError

def parse_structure(tokens):
    ast , _ = parse_scope(tokens)

    return ast

def parse_scope(tokens, index=0, indent_level=0, spaces_per_indent=None):
    ast = []

    while index < len(tokens):
        token, _ = read_token(["keyword", "newline"], tokens, index) 

        if token["type"] == "keyword":
            read_keyword(["SET", "USE", "SECTION", "INCLUDE"], tokens, index)
            keyword = token["text"]
            if keyword == "SET":
                node, index = parse_set_statement(tokens, index)
            elif keyword == "USE":
                node, index = parse_use_statement(tokens, index)
            elif keyword == "SECTION":
                node, index, spaces_per_indent = parse_section_statement(tokens, index, indent_level, spaces_per_indent)
            elif keyword == "INCLUDE":
                node, index = parse_include_statement(tokens, index)
            ast.append(node)
        if token["type"] == "newline":
            count, index = read_spaces(tokens, index+1)

            if not spaces_per_indent:
                if count != 0:
                    raise ParserError(f"unexpected indentation")
                continue
            current_spaces = indent_level * spaces_per_indent
            if count % spaces_per_indent != 0 or \
                    count > current_spaces:
                raise ParserError(f"unexpected indentation")
            if count < current_spaces:
                # we need to return the nl and eithe there
                # are spaces and its <nl> <space> <here>
                # or its <nl><here>
                space_offset = 2 if count else 1
                return ast, index-space_offset
            
    return ast, index

def parse_set_statement(tokens, index):
    _, index = read_keyword(["SET"], tokens, index)
    _, index = read_spaces(tokens, index)

    key_token, index = read_keyword(["TITLE", "SUBTITLE", "AUTHOR", "EXPLANATION", "DATE", "TOC"], tokens, index)
    _, index = read_spaces(tokens, index)

    value_token, index = read_token(["literal"], tokens, index)
    _, index = read_spaces(tokens, index)

    return {
        "type": "set_statement",
        "key": key_token["text"],
        "value": value_token["text"]
    }, index

def parse_use_statement(tokens, index):
    _, index = read_keyword(["USE"], tokens, index)
    _, index = read_spaces(tokens, index)

    path_token, index = read_token(["identifier"], tokens, index)
    _, index = read_spaces(tokens, index)

    fill_type = None

    next_token = tokens[index]
    if next_token["type"] == "keyword":
        token, index = read_keyword(["STRICT", "FILL"], tokens, index)
        _, index = read_spaces(tokens, index)
        fill_type = token["text"]

    return {
        "type": "use_statement",
        "path": path_token["text"],
        "fill_type": fill_type
    }, index

def parse_section_statement(tokens, index, indent_level, spaces_per_indent):
    _, index = read_keyword(["SECTION"], tokens, index)
    _, index = read_spaces(tokens, index)

    name_token, index = read_token(["literal"], tokens, index)

    count, _ = read_spaces(tokens, index+1)
    if count == 0:
        raise ParserError(f"expected indentation")
    if spaces_per_indent == None:
        spaces_per_indent = count

    section_ast, index = parse_scope(tokens, index, indent_level + 1, spaces_per_indent)

    return {
        "type": "section_statement",
        "name": name_token["text"],
        "contents": section_ast
    }, index, spaces_per_indent

def parse_include_statement(tokens, index):
    _, index = read_keyword(["INCLUDE"], tokens, index)
    _, index = read_spaces(tokens, index)

    path_token, index = read_token(["identifier"], tokens, index)
    _, index = read_spaces(tokens, index)

    return {
        "type": "include_statement",
        "path": path_token["text"]
    }, index

def read_keyword(expected_texts, tokens, index):
    _, index = read_spaces(tokens, index)

    read_token(["keyword"], tokens, index)

    token = tokens[index]
    token_text = token["text"]
    if token_text not in expected_texts:
        raise ParserError(f"expected {expected_texts}")
    
    return token, index + 1

def read_token(expected_types, tokens, index):
    _, index = read_spaces(tokens, index)

    token = tokens[index]
    token_type = token["type"]
    if token_type not in expected_types:
        raise ParserError(f"expected {expected_types}")

    return token, index + 1

def read_spaces(tokens, index):
    if index == len(tokens):
        return 0, index
    token = tokens[index]
    if token["type"] != "space":
        return 0, index
    return tokens[index]["count"], index + 1