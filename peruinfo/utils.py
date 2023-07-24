from re import sub


def to_camel(string: str) -> str:
    s = sub(r"(_|-)+", " ", string).title().replace(" ", "")
    return ''.join([s[0].lower(), s[1:]])
