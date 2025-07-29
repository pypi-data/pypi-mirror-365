class ViewsManagement:
    def __init__(self, client: "CloudabilityClient"):
        self._client = client

    def get_views(self):
        views = self._client._get("views")
        return(views)