import inspect
import sys
from abc import ABC

from .report import Report


class Reporter(ABC):

    def report(self, report):
        pass


class ReportManager(object):
    reporters = {}

    @classmethod
    def register(cls, reporter_clazz: Reporter, name, enabled):
        cls.reporters[name] = [reporter_clazz, enabled]

    @classmethod
    def enable(cls, names):
        """
        Enable only the given list of names and disable the rest.
        :param names: list of reporter names
        :return: None
        """
        for name, arr in cls.reporters.items():
            arr[1] = name in names

    @classmethod
    def report(cls, report: Report):
        for arr in cls.reporters.values():
            if arr[1]:
                # Report enabled
                arr[0]().report(report)
        if report.problem_count > 0:
            # Found problems. Mark the build as broken
            sys.exit(1)


def reporter(name, enabled=False):
    def _reporter(clazz):
        if inspect.isclass(clazz):
            if not hasattr(clazz, "report") or len(inspect.signature(getattr(clazz, "report")).parameters.items()) != 2:
                raise RuntimeError("Reporter must have a function 'report(self, report: Report)")
        else:
            raise RuntimeError("Reporter must be a class")

        # Register the reporter
        ReportManager.register(clazz, name, enabled)
        return clazz

    return _reporter
