keywords = [
    "SET",
    "TITLE",
    "SUBTITLE",
    "AUTHOR",
    "EXPLANATION",
    "DATE",
    "TOC",
    "USE",
    "SECTION",
    "INCLUDE",
    "STRICT"
]

def tokenize_structure(src):
    tokens = []
    index = 0
    while index < len(src):
        char = src[index]
        if char == "\"":
            token, index = parse_string_literal_token(src, index)
            tokens.append(token)
        elif char.isalpha():
            token, index = parse_keyword_token(src, index)
            tokens.append(token)
        elif char == "\n":
            tokens.append({"type": "newline"})
            index += 1
        elif char == " ":
            count = 0
            while src[index] == " ":
                index += 1
                count += 1
            tokens.append({"type": "space", "count": count})
        else:
            index += 1

    return tokens

def parse_keyword_token(src, index):
    start_index = index
    while index < len(src) and (not src[index].isspace()):
        index += 1
    text = src[start_index:index]
    token_type = "keyword" if text in keywords else "identifier"

    return {
        "type": token_type,
        "text": src[start_index:index]
    }, index

def parse_string_literal_token(src, index):
    start_index = index + 1
    end_index = src.index("\"", start_index)

    return {
        "type": "literal",
        "text": src[start_index:end_index]
    }, end_index + 1