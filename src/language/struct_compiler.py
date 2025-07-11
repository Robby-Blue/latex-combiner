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
                var_name = statement["key"]
                raise ParserError(f"doubled variables '{var_name}'")
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
            doc_folder_path = os.path.join(cwd, statement["path"])
            doc_path = os.path.join(doc_folder_path, "main.tex")
            if not os.path.exists(doc_path):
                raise ParserError(f"path {doc_folder_path} doesnt exist")
            structure.append({
                "type": "doc",
                "path": doc_path,
                "nest": nest_level
            })
            required_docs.remove(doc_folder_path)

    if required_docs:
        raise ParserError(f"required docs in {cwd} not used: {required_docs}")

    return {
        "variables": variables,
        "structure": structure,
        "required_docs": required_docs
    }