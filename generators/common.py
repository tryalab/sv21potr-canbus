def get_macros(node, mode, defines):
    macros = ''
    for define in defines:
        for index, name in enumerate(defines[define]):
            macros += f"#define {define.upper()}_{name} {index}\n"

    return macros
