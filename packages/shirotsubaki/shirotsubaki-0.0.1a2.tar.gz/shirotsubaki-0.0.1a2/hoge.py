if True:
    if True:
        import shirotsubaki.report

        report = shirotsubaki.report.ReportWithTabs()
        report.set('title', 'Fruits Fruits Fruits')
        report.add_tab('apple', 'apple apple')
        report.add_tab('banana', 'banana banana')
        report.add_tab('cherry', 'cherry cherry')
        report.output('docs/example_report_with_tabs.html')
