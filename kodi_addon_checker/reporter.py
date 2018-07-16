import inspect
from abc import ABC


class Reporter(ABC):

    def report(self, report):
        pass


class ReportManager(object):
    reporters = {}

    @classmethod
    def register(cls, reporter_clazz: Reporter, name, enabled):
        cls.reporters[name] = [reporter_clazz(), enabled]

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
    def getEnabledReporters(cls):
        return [reporter[0] for reporter in cls.reporters.values() if reporter[1]]


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
