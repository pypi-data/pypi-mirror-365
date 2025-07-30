class Style(dict):
    def __init__(self, d) -> None:
        super().__init__(d)

    def set(self, element: str, property: str, value: str) -> None:
        if element not in self:
            self[element] = {}
        self[element][property] = value

    def __str__(self) -> str:
        s = ''
        for k, v in self.items():
            s += k + ' {\n'
            for k_, v_ in v.items():
                s += f'  {k_}: {v_};\n'
            s += '}\n'
        return s[:-1]

    def __add__(self, other):
        if not isinstance(other, Style):
            raise TypeError(f'Unsupported operand types for +: Style and {type(other).__name__}')
        d = {k: v for k, v in self.items()}
        for k, v in other.items():
            if k in d:
                d[k] |= v
            else:
                d[k] = v
        return Style(d)

    @staticmethod
    def scrollable_table():
        """Styles for a scrollable table within a container. 

        Notes:
            The header row and the leftmost column are sticky.
            Wrap the table in <div class="table-container"></div>.
        """
        return Style({
            'th, td': {
                'border': '0',
            },
            '.table-container': {
                'overflow': 'auto',
                'white-space': 'nowrap',
                'max-height': '300px',
            },
            '.table-container table': {
                'border-collapse': 'separate',
                'border-spacing': '0',
                'width': '100%',
            },
            '.table-container thead th': {
                'border-top': '1px solid #303030',
                'border-bottom': '1px solid #303030',
                'padding-right': '0.5em',
                'text-align': 'left',
                'position': 'sticky',
                'top': '0',
                'background': '#f0f0f0',
                'z-index': '2',
            },
            '.table-container thead th:first-child': {
                'left': '0',
                'z-index': '3',
            },
            '.table-container tbody td': {
                'border-bottom': '1px solid #303030',
                'padding-right': '0.5em',
            },
            '.table-container tbody td:first-child': {
                'position': 'sticky',
                'left': '0',
                'background': '#ffffff',
                'z-index': '1',
            },
        })

    def add_scrollable_table(self) -> None:
        sty = self.__add__(Style.scrollable_table())
        self.update(sty)
