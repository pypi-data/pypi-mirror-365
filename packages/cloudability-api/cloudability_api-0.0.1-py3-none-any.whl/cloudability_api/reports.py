class ReportsAPI:
    def __init__(self, client: "CloudabilityClient"):
        self._client = client

    def get_reports(self):
        reports = self._client._get("reporting/reports/cost")
        return(reports)

    def get_measures(self, apply_allocations=False):
        if apply_allocations:
            measures = self._client._get("reporting/cost/measures", params={"apply_allocations": "true"})
        else:
            measures = self._client._get("reporting/cost/measures")
        return(measures)