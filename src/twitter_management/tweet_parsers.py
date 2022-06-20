def parse_tweet(content: str, val_script_dict):
    not_found = []
    for key, val in val_script_dict.items():
        val_to_search = "{" + str(key) + "}"

        new_content = content.replace(val_to_search, val)
        if new_content == content:
            not_found.append(key)

        content = new_content

    return content, not_found
