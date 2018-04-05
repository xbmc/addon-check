from kodi_addon_checker.common import colorPrint

from kodi_addon_checker.report import Reporter, Report, Record, reporter


@reporter(config_property="console-reporter", enabled=True)
class ConsoleReporter(Reporter):

    def report(self, report: Report):
        if type(report) is Record:
            if report.information:
                colorPrint(report, "34")
            elif report.warning:
                colorPrint(report, "35")
            elif report.problem:
                colorPrint(report, "31")
            else:
                print(report)
        else:
            print("\nChecking %s" % report.artifact_name)
            for rep in report:
                self.report(rep)
