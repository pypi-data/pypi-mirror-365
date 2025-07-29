class RightsizingAPI:
    def __init__(self, client: "CloudabilityClient"):
        self._client = client  # Has _get, _post, etc.

    def get_ec2_recommendations(self, params: dict = None):
        if params:
            self._client._validate_params(params)
        return self._client._get("rightsizing/aws/recommendations/ec2", params=params)

    def get_ec2_asg_recommendations(self, params: dict = None):
        if params:
            self._client._validate_params(params)
        return self._client._get("rightsizing/aws/recommendations/ec2-asg", params=params)