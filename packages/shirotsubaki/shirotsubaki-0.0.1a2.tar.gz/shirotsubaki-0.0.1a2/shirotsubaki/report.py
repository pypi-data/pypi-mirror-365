from abc import ABC, abstractmethod
from jinja2 import Environment, FileSystemLoader, meta
import importlib.resources
from shirotsubaki.style import Style


class ReportBase(ABC):
    @abstractmethod
    def __init__(self, title=None) -> None:
        template_dir = importlib.resources.files('shirotsubaki').joinpath('templates')
        self.env = Environment(loader=FileSystemLoader(template_dir))
        self.style = Style({
            'body': {
                'margin': '20px',
                'color': '#303030',
                'font-family': '\'Verdana\', \'BIZ UDGothic\', sans-serif',
                'font-size': '90%',
                'line-height': '1.3',
                'letter-spacing': '0.02em',
            },
            'table': {
                'border-collapse': 'collapse',
            },
            'th, td': {
                'border': '1px solid #303030',
                'padding': '0.2em 0.4em',
            },
        })
        self._data = {}
        self.keys_list = []
        self.keys_reserved = ['style']
        if title is not None:
            self.set('title', title)

    def set(self, key, value) -> None:
        if (key in self.keys_reserved) or (key in self.keys_list):
            print(f'Key \'{key}\' is not allowed to be set.')
            return
        self._data[key] = value

    def append_to(self, key, value) -> None:
        if key not in self.keys_list:
            print(f'Key \'{key}\' is not allowed to be append.')
            return
        self._data[key].append(value)

    def output(self, out_html) -> None:
        self._data['style'] = str(self.style)
        for key in self.keys_list:
            self._data[key] = '\n'.join([str(v) for v in self._data[key]])
        with open(out_html, 'w', encoding='utf8', newline='\n') as ofile:
            ofile.write(self.template.render(self._data))


class Report(ReportBase):
    """A class for creating a simple report.

    Example:
        ```python
        import shirotsubaki.report
        from shirotsubaki.element import Element as Elm

        rp = shirotsubaki.report.Report(title='Fruits')
        rp.style.set('h1', 'color', 'steelblue')
        rp.append(Elm('h1', 'Fruits Fruits'))
        rp.append('Fruits Fruits Fruits')
        rp.output('docs/example_report.html')
        ```

        [example_report.html](../example_report.html)
    """
    def __init__(self, title=None) -> None:
        super().__init__(title)
        self.template = self.env.get_template('report.html')
        self._data['content'] = []
        self.keys_list.append('content')

    def append(self, value) -> None:
        self.append_to('content', value)


class ReportWithTabs(ReportBase):
    """A class for creating a report with tabs.

    Example:
        ```python
        import shirotsubaki.report

        rp = shirotsubaki.report.ReportWithTabs()
        rp.set('title', 'Fruits Fruits Fruits')
        rp.add_tab('apple', 'apple apple')
        rp.add_tab('banana', 'banana banana')
        rp.add_tab('cherry', 'cherry cherry')
        rp.output('docs/example_report_with_tabs.html')
        ```

        [example_report_with_tabs.html](../example_report_with_tabs.html)
    """
    def __init__(self, title=None) -> None:
        super().__init__(title)
        self.template = self.env.get_template('report_with_tabs.html')
        self.style.set('body', 'margin', '0')
        self.tabs = {}
        self.keys_reserved.append('tabs')

    def add_tab(self, key, content=None) -> None:
        if key in self.tabs:
            raise KeyError(f'Tab \'{key}\' already exists.')
        self.tabs[key] = [content] if content else []

    def append_to_tab(self, key, value) -> None:
        if key not in self.tabs:
            self.add_tab(key)
        self.tabs[key].append(value)

    def _create_elements(self) -> None:
        selectors_comb = []
        selectors_has = []
        elements_radio = []
        elements_label = []
        for i, label in enumerate(self.tabs):
            selectors_comb.append(f'#btn{i:02}:checked ~ #tab{i:02}')
            selectors_has.append(f':has(#btn{i:02}:checked) .header label[for="btn{i:02}"]')
            elements_radio.append(f'<input type="radio" name="tab" id="btn{i:02}" hidden/>')
            elements_label.append(f'<label for="btn{i:02}">{label}</label>')
        elements_radio[0] = elements_radio[0].replace('hidden', 'hidden checked')
        self.set('selectors_comb', ',\n'.join(selectors_comb))
        self.set('selectors_has', ',\n'.join(selectors_has))
        self.set('elements_radio', '\n'.join(elements_radio))
        self.set('elements_label', '\n'.join(elements_label))

    def output(self, out_html) -> None:
        self._create_elements()
        for key in self.tabs:
            self.tabs[key] = '\n'.join([str(v) for v in self.tabs[key]])
        self._data['tabs'] = self.tabs
        super().output(out_html)
