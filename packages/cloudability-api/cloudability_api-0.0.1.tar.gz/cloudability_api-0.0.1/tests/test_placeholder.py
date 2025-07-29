from cloudability_api import CloudabilityClient
from os import getenv

def test_client_instantiation():
    client = CloudabilityClient(api_key="dummy_key")
    assert client.api_key == "dummy_key"

def test_ec2():
    api_key_from_env = getenv("CLOUDABILITY_API_KEY")
    client = CloudabilityClient(api_key=api_key_from_env)
    response = client.rightsizing.get_ec2_recommendations(params={"viewId": 0, "offset" :0, "limit": 10})

def test_ec2_asg():
    api_key_from_env = getenv("CLOUDABILITY_API_KEY")
    client = CloudabilityClient(api_key=api_key_from_env)
    response = client.rightsizing.get_ec2_asg_recommendations(params={"viewId": 0, "offset" :0, "limit": 10})

def test_reports():
    api_key_from_env = getenv("CLOUDABILITY_API_KEY")
    client = CloudabilityClient(api_key=api_key_from_env)
    response = client.reports.get_reports()

def test_reports_measures():
    api_key_from_env = getenv("CLOUDABILITY_API_KEY")
    client = CloudabilityClient(api_key=api_key_from_env)
    response_with_allocations = client.reports.get_measures(apply_allocations=True)
    response_without_allocations = client.reports.get_measures()

def test_rightsizing_roi():
    api_key_from_env = getenv("CLOUDABILITY_API_KEY")
    client = CloudabilityClient(api_key=api_key_from_env)
    response = client.rightsizingroi.get_roi_tickets()

def test_rightsizing_roi_with_limit():
    params={"offset":0, "limit":10}
    api_key_from_env = getenv("CLOUDABILITY_API_KEY")
    client = CloudabilityClient(api_key=api_key_from_env)
    response = client.rightsizingroi.get_roi_tickets(params=params)