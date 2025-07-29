class RightsizingROI:
    def __init__(self, client: "CloudabilityClient"):
        self._client = client  # Has _get, _post, etc.

    def get_roi_tickets(self, params : dict = None):
        if params:
            self._client._validate_params(params)
        return self._client._get("rightsizing-roi/actioned", params=params)