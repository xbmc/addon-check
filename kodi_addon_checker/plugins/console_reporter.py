from kodi_addon_checker.record import INFORMATION, WARNING, PROBLEM
from kodi_addon_checker.report import Record
from kodi_addon_checker.reporter import Reporter, reporter


def colorPrint(string, color):
    """
    Utility function to print message to console.
    :param string: the message to print
    :param color: message color
    :return:
    """
    print("\033[%sm%s\033[0m" % (color, string))


@reporter(name="console", enabled=True)
class ConsoleReporter(Reporter):

    def report(self, report):
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
