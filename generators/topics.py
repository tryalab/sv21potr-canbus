def get_topics(nodes):
    text = ""

    for node in nodes.values():
        name = node.get("name")
        for key_signal, value_signal in node.items():
            if type(value_signal) is not dict:
                if key_signal != "name":
                    text += f'"/{name}/{key_signal}",\n'
            else:
                for key_inside_signal, value_inside_signal in value_signal.items():
                    if type(value_inside_signal) is not dict:
                        text += f'"/{name}/{key_signal}/{key_inside_signal}",\n'
                    else:
                        for min_max, value_min_max in value_inside_signal.items():
                            if type(value_min_max) is not dict:
                                text += f'"/{name}/{key_signal}/{key_inside_signal}/{min_max}",\n'
                            else:
                                for key_inside_min_max, value_inside_min_max in value_min_max.items():
                                    if type(value_inside_min_max) is not dict:
                                        text += f'"/{name}/{key_signal}/{key_inside_signal}/{min_max}/{key_inside_min_max}",\n'
            
    text_total = f"""\
char topics[60][50] ={{
    {text[:-2]}}}"""

    return text_total