import re

def parse(content, **kwargs):
    patterns = [r'<p>(<img.*?>)</p>', r'<p>(<embed.*?>)</p>']
    parsed = content

    for pattern in patterns:
        ex = re.compile(pattern)
        groups = ex.findall(parsed)
        for item in groups:
            result = '<p><i>' + item + '</i></p>'
            item = re.escape(item)
            parsed = re.sub(r'<p>' + item + r'</p>', result, parsed)
    return parsed