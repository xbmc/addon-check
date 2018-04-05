from kodi_addon_checker.common import colorPrint

from kodi_addon_checker.report import Reporter, Report, Record, reporter, INFORMATION, WARNING, PROBLEM


@reporter(config_property="console-reporter", enabled=True)
class ConsoleReporter(Reporter):

    def report(self, report: Report):
        if type(report) is Record:
            if report.log_level == INFORMATION:
                colorPrint(report, "34")
            elif report.log_level == WARNING:
                colorPrint(report, "35")
            elif report.log_level == PROBLEM:
                colorPrint(report, "31")
        else:
            for rep in report:
                self.report(rep)
