def get_macros(values, defines):
    macros = ''
    for define in defines:
        if define in values:
            for index, name in enumerate(defines[define]):
                macros += f"#define {define.upper()}_{name} {index}\n"
    return macros
