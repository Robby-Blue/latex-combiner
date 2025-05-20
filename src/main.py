import sys
import os
import hashlib

import doc_rewriter
import language

def rewrite_doc(doc_path, nest):
    md5_hash = hash_path(doc_path)
    file_name = f"{md5_hash}.tex"
    output_file = os.path.join("output", file_name)

    with open(doc_path, "r") as f:
        src = f.read()

    # if this becomes too slow make a package cache to read from
    output_src, packages = doc_rewriter.rewrite_document(src, nest)

    if (os.path.exists(output_file) and
            os.path.getmtime(doc_path) > os.path.getmtime(output_file)):
        return packages

    with open(output_file, "w") as f:
        f.write(output_src)

    return packages

def rewrite_docs(documents):
    total_packages = {}

    for document in documents:
        document_path = document["path"]
        nest = document["nest"]
        print(nest)
        packages = rewrite_doc(document_path, nest)

        for package in packages:
            name = package["name"]
            line = package["line"]
            if name in total_packages:
                if line != total_packages[name]:
                    print(f"bad package {name}")
                    exit(1)
            else:
                total_packages[name] = line

    return total_packages

def rewrite_main(packages, variables):
    dir = os.path.dirname(__file__)
    with open(os.path.join(dir, "template.tex")) as f:
        src = f.read()

    src = src.replace("\\$title\\$", variables.get("TITLE", ""))
    src = src.replace("\\$author\\$", variables.get("AUTHOR", ""))
    src = src.replace("\\$date\\$", variables.get("DATE", ""))

    has_title = bool(variables.get("TITLE", ""))
    startpage_code = "\\maketitle" if has_title else ""
    src = src.replace("\\$maketitle\\$", startpage_code)

    has_toc = variables.get("TOC", "false") == "true"
    startpage_code = "\\tableofcontents" if has_toc else ""
    src = src.replace("\\$toc\\$", startpage_code)

    package_imports = ""
    for package_line in packages.values():
        package_imports += f"{package_line}\n"

    src = src.replace("\\$package_imports\\$", package_imports)

    last_nest = 0
    contents = ""
    section_types = ["section", "subsection", "subsubsection"]
    for node in structure:
        if node["type"] == "section":
            nest = node["nest"]
            section_type = section_types[node["nest"]]
            text = node["text"]
            if nest <= last_nest:
                contents += "\\newpage\n"
            contents += "\\"+section_type+"{"+text+"}\n"
            last_nest = nest
        if node["type"] == "doc":
            hash = hash_path(node["path"])
            contents += "\\input{"+hash+"}\n"

    src = src.replace("\\$contents\\$", contents)

    with open("output/main.tex", "w") as f:
        f.write(src)

def hash_path(path):
    return hashlib.md5(path.encode("UTF8")).hexdigest()

structure_file = sys.argv[1]
res = language.parse_file(structure_file)

structure = res["structure"]
variables = res["variables"]

documents = [node for node in structure if node["type"] == "doc"]

packages = rewrite_docs(documents)
rewrite_main(packages, variables)