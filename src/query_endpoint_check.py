import sys
import boto3
import requests
import json
import os

"""
Wrapper to call Cloudwatch put metric function
"""
def put_metric_wrapper(cloudwatch, namespace, metric_name, dim_name, dim_value, value):
    cloudwatch.put_metric_data(
        Namespace=namespace,
        MetricData=[
            {
                'MetricName': metric_name,
                'Dimensions': [
                    {
                        'Name': dim_name,
                        'Value': dim_value
                    },
                ],
                'Value': value
            },
        ]
    )


"""
Send POST request to Query endpoint
"""
def send_post_request(url, json_data, username, password, headers):
    return requests.post(url, data=json_data, auth=(username, password), headers=headers)


"""
Checks response status of POST request to Query endpoint
If an 200 response status is received, record a value of 1.0 in cloudwatch
Else, record a value of 0.0 in cloudwatch
"""
def check_query_endpoint(url, json_data, username, password):
    response=send_post_request(url, json_data, username, password, {'content-type':'application/json'})
	
    cloudwatch = boto3.client('cloudwatch')	
	
    if response.status_code == 200:
        put_metric_wrapper(
		                    cloudwatch, 
                            'query-endpoint', 
                            'query_endpoint_check', 
                            'HealthCheck', 
                            'QueryEndpoint', 
                            1.0
                          )
    else:
        put_metric_wrapper(
		                    cloudwatch, 
                            'query-endpoint', 
                            'query_endpoint_check', 
                            'HealthCheck', 
                            'QueryEndpoint', 
                            0.0
                          )
	
def main():
    try:
        username = os.environ["USERNAME"]
        password = os.environ["PASSWORD"]
        query_url = os.environ['QUERY_URL']
    except:
        raise Exception('Missing environment variable: USERNAME, PASSWORD, or QUERY_URL')
	
	
    raw_query = {
        "systemQueryName": "SDW 2.3",
        "resultEncoding": "hex",
        "resultPackaging": "none",
        "orderByField": "none",
        "orderByOrder": "ascending",
        "skip": 0,
        "limit": 0,
        "dialogId": "advSitDataDep",
        "nwLat": 84.2,
        "nwLon": 80.1,
        "seLat": 40.3,
        "seLon": 60.5,
        "startDate": "2014-09-16T14:25:07.609Z",
        "startDateOperator": "GTE",
        "endDate": "2014-09-19T14:45:07.609Z",
        "endDateOperator": "LTE"
    }
    query_as_json=json.dumps(raw_query)
	
    check_query_endpoint(query_url, query_as_json, username, password)


if __name__ == '__main__':
    main()
