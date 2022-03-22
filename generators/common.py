def get_common_header(values):
    macros = ''
    name_list = []

    for value in values:
        for index, name in enumerate(value):
            if name not in name_list:
                name_list.append(name)
                macros += f"#define {name} {index}\n"

    header_content = f"""\
#ifndef COMMON_H
#define COMMON_H
    
{macros}
#endif /* COMMON_H */"""

    return header_content
