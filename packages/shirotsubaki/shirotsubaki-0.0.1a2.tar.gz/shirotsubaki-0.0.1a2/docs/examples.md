# Examples

Here are some examples of how to use this package:

## Example 1

<a href="../example_1.html" class="asis" target="_blank" rel="noopener noreferrer">example_1.html</a>

```python
import shirotsubaki.report
from shirotsubaki.element import Element as Elm

def create_table():
    tbl = Elm('table')
    thead = Elm('thead')
    tbody = Elm('tbody')

    thead.append(Elm('tr'))
    for _ in range(5):
        thead.inner[-1].append(Elm('th', 'apple'))
        thead.inner[-1].append(Elm('th', 'banana'))
        thead.inner[-1].append(Elm('th', 'cherry'))
    for i in range(20):
        tbody.append(Elm('tr'))
        for _ in range(5):
            tbody.inner[-1].append(Elm('td', 'apple'))
            tbody.inner[-1].append(Elm('td', 'banana'))
            tbody.inner[-1].append(Elm('td', 'cherry'))

    tbl.append(thead)
    tbl.append(tbody)
    div = Elm('div', tbl).set_attr('class', 'table-container')
    return div

report = shirotsubaki.report.ReportWithTabs()
report.style.add_scrollable_table()
report.set('title', 'Fruits Fruits Fruits')
report.append_to_tab('apple', Elm('h2', 'apple apple apple'))
for _ in range(5):
    report.append_to_tab('apple', Elm('h3', 'table'))
    report.append_to_tab('apple', create_table())
report.append_to_tab('banana', 'banana banana')
report.append_to_tab('cherry', 'cherry cherry')
report.output('docs/example_1.html')
```
