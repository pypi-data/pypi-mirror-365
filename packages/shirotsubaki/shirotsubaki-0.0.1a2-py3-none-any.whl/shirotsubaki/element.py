class Element:
    def __init__(self, tagname: str, content=None) -> None:
        self.tagname = tagname
        self.attrs = {}
        self.inner = [content] if content else []

    def set_attr(self, key: str, value: str) -> 'Element':
        self.attrs[key] = value
        return self

    def append(self, elm) -> None:
        self.inner.append(elm)

    def __str__(self) -> str:
        attrs_str = ''.join([f' {k}="{v}"' for k, v in self.attrs.items()])
        s = f'<{self.tagname}{attrs_str}>\n'
        for elm in self.inner:
            if isinstance(elm, str):
                s += elm + '\n'
            else:
                s += str(elm)
        s += f'</{self.tagname}>\n'
        return s
