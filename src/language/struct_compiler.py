import os

from language.parser_error import ParserError

def compile_structure(ast):
    variables = {}

    for statement in ast:
        statement_type = statement["type"]
        if statement_type == "set_statement":
            if statement["key"] in variables:
                var_name = statement["key"]
                raise ParserError(f"doubled variables '{var_name}'")
            variables[statement["key"]] = statement["value"]
        elif statement_type == "include_statement":
            doc_folder_path = statement["path"]
            doc_path = os.path.join(doc_folder_path, "main.tex")
            if not os.path.exists(doc_path):
                raise ParserError(f"path {doc_folder_path} doesnt exist")
            structure.append({
                "type": "doc",
                "path": doc_path,
                "nest": 0
            })

    structure = compile_section(ast, "", 0)

    return {
        "structure": structure,
        "variables": variables
    }

def compile_section(ast, base_path, nest_level):
    structure = []
    required_docs = []

    cwd = base_path

    for statement in ast:
        statement_type = statement["type"]
        if statement_type == "use_statement":
            cwd = os.path.join(base_path, statement["path"])
            fill_type = statement["fill_type"]
            required_docs.append({
                "cwd": cwd,
                "fill_type": fill_type,
                "paths": get_docs_in_folder(cwd)
            })
        elif statement_type == "section_statement":
            structure.append({
                "type": "section",
                "text": statement["name"],
                "nest": nest_level
            })

            structure += compile_section(statement["contents"], cwd, nest_level+1)
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
            required_docs[-1]["paths"].remove(doc_folder_path)

    for required_folder in required_docs:
        last_fill_type = required_folder["fill_type"]
        if last_fill_type == None:
            pass
        elif last_fill_type == "STRICT":
            if len(required_folder["paths"]):
                raise ParserError(f"required docs in {cwd} not used: {required_docs}")
        elif last_fill_type == "FILL":
            for required_path in required_folder["paths"]:
                print("filled in", os.path.basename(required_path))
                doc_path = os.path.join(required_path, "main.tex")
                structure.append({
                    "type": "doc",
                    "path": doc_path,
                    "nest": nest_level
                })
        else:
            raise ParserError(f"bad fill type")
        
    return structure

def get_docs_in_folder(cwd):
    paths = set()
    for name in os.listdir(cwd):
        doc_path = os.path.join(cwd, name)
        paths.add(doc_path)
    return paths