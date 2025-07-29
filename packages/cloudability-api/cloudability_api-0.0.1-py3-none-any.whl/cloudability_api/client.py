import requests
from requests.auth import HTTPBasicAuth
from .rightsizing import RightsizingAPI
from .reports import ReportsAPI
from .views import ViewsManagement
from .rightsizing_roi import RightsizingROI

class CloudabilityClient:
    def __init__(self, api_key: str, base_url: str = "https://api.cloudability.com/v3/"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()

        self.session.auth = HTTPBasicAuth(self.api_key + ":", "")
        self.session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json",
        })

        # Pass full client reference
        self.rightsizing = RightsizingAPI(self)
        self.rightsizingroi = RightsizingROI(self)
        self.reports = ReportsAPI(self)
        self.views = ViewsManagement(self)

    def _validate_params(self, params: dict = None):
        allowed_keys = {"filter",
                        "limit",
                        "offset",
                        "sort",
                        "viewId"}
        for key in params.keys():
            if key not in allowed_keys:
                raise ValueError(f"Invalid parameter: {key}. Allowed keys are: {allowed_keys}")
            if key == "offset":
                if "limit" in params.keys():
                    pass
                else:
                    raise ValueError("Missing limit value in params")
            if key == "limit":
                if "offset" in params.keys():
                    pass
                else:
                    raise ValueError("Missing offset value in params")


    def _get(self, path: str, params: dict = None):
        url = f"{self.base_url}{path}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def _post(self, path: str, data: dict = None):
        url = f"{self.base_url}{path}"
        response = self.session.post(url, json=data)
        response.raise_for_status()
        return response.json()
