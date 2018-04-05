import inspect
from abc import ABC

PROBLEM = "ERROR"
WARNING = "WARN"
INFORMATION = "INFO"

KODI_REPORTERS = {}


class Report(object):
    def __init__(self):
        self.problem_count = 0
        self.warning_count = 0
        self.information_count = 0
        self.reports = []

    def log(self, report):
        self.reports.append(report)
        if type(report) is Record:
            if PROBLEM == report.log_level:
                self.problem_count += 1
            elif WARNING == report.log_level:
                self.warning_count += 1
            else:
                self.information_count += 1
        else:
            self.problem_count += report.problem_count
            self.warning_count += report.warning_count
            self.information_count += report.information_count

    def __iter__(self):
        return iter(self.reports)


class Record(Report):
    def __init__(self, log_level, message, start_line=-1, end_line=-1, start_char_position=-1,
                 end_char_position=-1):
        self.log_level = log_level
        self.message = message
        self.start_line = start_line
        self.end_line = end_line
        self.start_char_position = start_char_position
        self.end_char_position = end_char_position

    def log(self, record):
        pass

    def __str__(self):
        """
        Text representation of record.
        :return: text representation of report
        """
        if self.start_line == -1:
            return "%s: %s" % (self.log_level, self.message)
        elif self.start_char_position == -1:
            return "%s [%d-%d]: %s" % (self.log_level, self.start_line, self.end_line, self.message)
        else:
            return "%s [%d:%d-%d:%d]: %s" % (
                self.log_level, self.start_line, self.start_char_position, self.end_line, self.end_char_position,
                self.message)


class Reporter(ABC):

    def report(self, report: Report):
        pass


def reporter(config_property, enabled=False):
    def _reporter(clazz):
        if inspect.isclass(clazz):
            if not hasattr(clazz, "report") or len(inspect.signature(getattr(clazz, "report")).parameters.items()) != 2:
                raise RuntimeError("Reporter must have a function 'report(self, report: Report)")
        else:
            raise RuntimeError("Reporter must be a class")
        KODI_REPORTERS[config_property] = [clazz, enabled]
        return clazz

    return _reporter
