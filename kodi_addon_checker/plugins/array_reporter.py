from kodi_addon_checker.report import Record
from kodi_addon_checker.reporter import Reporter, reporter


@reporter(name="array", enabled=False)
class ArrayReporter(Reporter):
    def __init__(self):
        self.reports = []

    def report(self, report):
        if type(report) is Record:
            self.reports.append(report)
