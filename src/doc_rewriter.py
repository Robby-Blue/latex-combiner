def rewrite_document(src, nest):
    # makes it not put equations into the page numbers
    # without breaking wrapfig
    src = src.replace("\\[", "\\vspace{0pt}\\[")

    src = remove_commands(src, [r"\documentclass{article}",
        r"\begin{document}", r"\end{document}"])
    src, packages = find_and_remove_packages(src)
    src = fix_sections(src, nest)
    src = undefine_custom_commands(src)
    src = find_and_remove_headers(src)

    return src, packages

def find_and_remove_packages(src):
    packages = []
    offset = 0

    indexed_commands = find_indexed_commands(src, ["usepackage"])
    for index, _ in indexed_commands:
        index += offset
        next_command_start = src.index("\\", index+1)

        packages.append(parse_package(src[index:next_command_start]))

        command_length = next_command_start - index
        src, offset_change = replace_text("",
                index, command_length, src)

        offset += offset_change

    return src, packages

def find_and_remove_headers(src):
    offset = 0

    indexed_commands = find_indexed_commands(src, ["lhead", "rhead"])
    for index, _ in indexed_commands:
        index += offset
        next_command_start = src.index("\\", src.index("\n", index+1))

        command_length = next_command_start - index
        src, offset_change = replace_text("",
                index, command_length, src)

        offset += offset_change

    return src

def undefine_custom_commands(src):
    indexed_commands = find_indexed_commands(src, ["newcommand"])
    for index, _ in indexed_commands:
        command = src[src.index("{", index)+1:src.index("}", index)]

        src += fr"\let{command}\undefined"
    
    return src

def parse_package(src):
    name_start_index = src.index("{")
    name_end_index = src.index("}")
    name = src[name_start_index+1:name_end_index] 

    return {
        "name": name,
        "line": src.strip()
    }

def fix_sections(src, nest):
    """
    moves section hierarchy down by two levels
    because theres expected to be two levels of documents
    above each document
    """
    
    relevant_commands = [
        "section",
        "subsection"
    ]

    offset = 0
    indexed_commands = find_indexed_commands(src, relevant_commands)
    for index, command in indexed_commands:
        index += offset
        command_length = len(command)

        replacement_command = get_replacement_command(command, nest)

        new_command_call = f"\n\\{replacement_command}"
        src, offset_change = replace_text(new_command_call,
                index, command_length+1, src)

        offset += offset_change

    return src

def remove_commands(src, commands):
    for command in commands:
        src = src.replace(command, "")
    return src

def replace_text(new_text, start_index, length, src):
    """replace text at a specific index, while being aware of the offset this causes"""

    end_index = start_index + length

    src = src[:start_index] + new_text + src[end_index:]
    
    return src, len(new_text) - length

def get_replacement_command(command, nest):
    if command in ["section", "section*"]:
        level = 0
    if command in ["subsection", "subsection*"]:
        level = 1
    level += nest
    return "document"+"sub"*level+"section"

def find_indexed_commands(src, commands):
    found_commands = []
    index = 0

    while True:
        found_index = None
        found_command = None
        for command in commands:
            for suffix in ["[", "{", "*[", "*{"]:
                effective_command = "\\"+command+suffix
                if effective_command not in src[index+1:]:
                    continue
                command_index = src.index(effective_command, index+1)
                if found_index is None or command_index < found_index:
                    found_index = command_index
                    found_command = command + suffix[:-1]

        if found_index is None:
            break

        index = found_index
        found_commands.append((index, found_command))

    return found_commands