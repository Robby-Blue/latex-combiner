import os

from language.parser_error import ParserError

def compile_structure(ast, base_path="", nest_level=0):
    variables = {}
    structure = []
    required_docs = set()

    cwd = base_path

    for statement in ast:
        statement_type = statement["type"]
        if statement_type == "set_statement":
            if statement["key"] in variables:
                raise ParserError("doubled variables")
            if nest_level != 0:
                raise ParserError("variables must be at top level")
            variables[statement["key"]] = statement["value"]
        elif statement_type == "use_statement":
            cwd = os.path.join(base_path, statement["path"])
            if not statement["is_strict"]:
                continue
            for name in os.listdir(cwd):
                doc_path = os.path.join(cwd, name)
                required_docs.add(doc_path)
        elif statement_type == "section_statement":
            structure.append({
                "type": "section",
                "text": statement["name"],
                "nest": nest_level
            })

            section = compile_structure(statement["contents"], cwd, nest_level+1)
            structure += section["structure"]
            required_docs.update(section["required_docs"])
        elif statement_type == "include_statement":
            doc_path = os.path.join(cwd, statement["path"])
            if not os.path.exists(doc_path):
                raise ParserError("path doesnt exist")
            structure.append({
                "type": "doc",
                "text": doc_path,
                "nest": nest_level
            })
            required_docs.remove(doc_path)

    if required_docs:
        raise ParserError("required doc not used")

    return {
        "variables": variables,
        "structure": structure,
        "required_docs": required_docs
    }