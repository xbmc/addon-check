from kodi_addon_checker.record import Record, PROBLEM, WARNING


class Report(object):
    def __init__(self, artifact_name):
        """
        Create a new report for the given artifact. The artifact can be a repo, add-on or file.
        :param artifact_name: the artifact name
        """
        self.artifact_name = artifact_name
        self.problem_count = 0
        self.warning_count = 0
        self.information_count = 0
        self.reports = []

    def add(self, report):
        """
        Add a sub record/report to this report.
        :param report: a record or report
        :return: None
        """
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
