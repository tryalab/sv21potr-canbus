def get_common_header(values, defines):
    macros = ''

    for define in defines:
        if define in values:
            for index, name in enumerate(defines[define]):
                macros += f"#define {define.upper()}_{name} {index}\n"

    header_content = f"""\
#ifndef COMMON_H
#define COMMON_H
    
{macros}
#endif /* COMMON_H */"""

    return header_content
