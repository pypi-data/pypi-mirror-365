import shirotsubaki.report
import shirotsubaki.utils
from shirotsubaki.style import Style as Sty
from shirotsubaki.element import Element as Elm
import os


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


def test_lighten_color():
    color = shirotsubaki.utils.lighten_color('#336699')
    assert color == '#99B2CC'


def test_report():
    rp = shirotsubaki.report.Report(title='Fruits')
    rp.style.set('h1', 'color', 'steelblue')
    rp.style.add_scrollable_table()
    rp.append(Elm('h1', 'Fruits'))
    rp.append(create_table())
    rp.output('my_report.html')
    os.remove('my_report.html')


def test_report_with_tabs():
    rp = shirotsubaki.report.ReportWithTabs()
    rp.style.add_scrollable_table()
    rp.set('title', 'Fruits Fruits Fruits')
    rp.add_tab('apple', 'apple apple')
    rp.add_tab('banana', 'banana banana')
    rp.add_tab('cherry', 'cherry cherry')
    for _ in range(5):
        rp.append_to_tab('cherry', Elm('h3', 'table'))
        rp.append_to_tab('cherry', create_table())
    rp.output('my_report_with_tabs.html')
    os.remove('my_report_with_tabs.html')


def test_style():
    sty0 = Sty({'body': {'color': 'red'}})
    sty1 = Sty({'body': {'background': 'pink'}})
    sty2 = Sty({'body': {'color': 'blue'}})

    sty0 += sty1
    assert sty0['body']['color'] == 'red'
    assert sty0['body']['background'] == 'pink'

    sty0 += sty2
    assert sty0['body']['color'] == 'blue'
    assert sty0['body']['background'] == 'pink'

    sty0.add_scrollable_table()
    print(str(sty0))
