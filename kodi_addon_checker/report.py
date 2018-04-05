import inspect
from abc import ABC

PROBLEM = "ERROR"
WARNING = "WARN"
INFORMATION = "INFO"

KODI_REPORTERS = {}


class Report(object):
    def __init__(self, artifact_name):
        self.artifact_name = artifact_name
        self.problem = 0
        self.warning = 0
        self.information = 0
        self.reports = []

    def log(self, report):
        self.reports.append(report)
        self.problem += report.problem
        self.warning += report.warning
        self.information += report.information

    def __iter__(self):
        return iter(self.reports)


class Record(Report):
    def __init__(self, artifact_name, message, start_line=-1, end_line=-1, start_char_position=-1,
                 end_char_position=-1):
        super().__init__(artifact_name)
        self.message = message
        self.start_line = start_line
        self.end_line = end_line
        self.start_char_position = start_char_position
        self.end_char_position = end_char_position

        if PROBLEM == artifact_name:
            self.problem = 1
        elif WARNING == artifact_name:
            self.warning = 1
        else:
            self.information = 1

    def log(self, record):
        pass

    def __str__(self):
        """
        Text representation of record.
        :return: text representation of report
        """
        if self.start_line == -1:
            return "%s: %s" % (self.artifact_name, self.message)
        elif self.start_char_position == -1:
            return "%s [%d-%d]: %s" % (self.artifact_name, self.start_line, self.end_line, self.message)
        else:
            return "%s [%d:%d-%d:%d]: %s" % (
                self.artifact_name, self.start_line, self.start_char_position, self.end_line, self.end_char_position,
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
