import sys
import os
import hashlib

import doc_rewriter
import language

title = "Example Document"
author = "John Doe"
date = "Today"

documents = []

def rewrite_doc(doc_path):
    input_file = os.path.join("input", doc_path)

    md5_hash = hashlib.md5(doc_path.encode("UTF8")).hexdigest()
    file_name = f"{md5_hash}.tex"
    output_file = os.path.join("output", file_name)

    with open(input_file, "r") as f:
        src = f.read()

    # if this becomes too slow make a package cache to read from
    output_src, packages = doc_rewriter.rewrite_document(src)

    if (os.path.exists(output_file) and
            os.path.getmtime(input_file) > os.path.getmtime(output_file)):
        return md5_hash, packages

    with open(output_file, "w") as f:
        f.write(output_src)

    return md5_hash, packages

def rewrite_docs():
    doc_file_names = []
    total_packages = {}

    for document in documents:
        name, packages = rewrite_doc(document)
        doc_file_names.append(name)

        for package in packages:
            name = package["name"]
            line = package["line"]
            if name in total_packages:
                if line != total_packages[name]:
                    print(f"bad package {name}")
                    exit(1)
            else:
                total_packages[name] = line

    return doc_file_names, total_packages

def rewrite_main(doc_file_names, packages):
    dir = os.path.dirname(__file__)
    with open(os.path.join(dir, "template.tex")) as f:
        src = f.read()

    src = src.replace("\$title\$", title)
    src = src.replace("\$author\$", author)
    src = src.replace("\$date\$", date)

    package_imports = ""
    for package_line in packages.values():
        package_imports += f"{package_line}\n"

    src = src.replace("\$package_imports\$", package_imports)

    contents = ""
    for file_name in doc_file_names:
        contents += "\include{"+file_name+"}\n"
    src = src.replace("\$contents\$", contents)

    with open("output/main.tex", "w") as f:
        f.write(src)

structure_file = sys.argv[1]
language.parse_file(structure_file)

# doc_file_names, packages = rewrite_docs()
# rewrite_main(doc_file_names, packages)