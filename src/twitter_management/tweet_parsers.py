def parse_tweet(content: str, val_script_dict):
    """Function parses tweet content and returns converted variables replaced by its walues
    
    Parameters:
        content(str): content of Tweet to be converted
        val_script_dict(dict(str, str)): dictionary with variable name - value pais
    Returns:
        pair(str, List[str]): pair of converted content and list of unmatched variables"""
    not_found = []
    for key, val in val_script_dict.items():
        val_to_search = "{" + str(key) + "}"

        new_content = content.replace(val_to_search, val)
        if new_content == content:
            not_found.append(key)

        content = new_content

    return content, not_found
