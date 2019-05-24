#!/usr/bin/python

import boto3
import requests
import requests
import datetime
import os


"""
Wrapper to call Cloudwatch put metric function
"""
def put_metric_data_wrapper(cloudwatch, namespace, metric_name, dim_name, dim_value, value):
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
Checks response status of HEAD request
If a 302 response status is received, record a value of 1.0 in cloudwatch
Else, record a value of 0.0 in cloudwatch
"""
def test_nginx_redirect(url):
    cloudwatch = boto3.client('cloudwatch')
    resp = requests.head(url)
	
    if resp.status_code == 302:
        put_metric_data_wrapper(
                                    cloudwatch, 
                                    'nginx', 
                                    'nginx_redirect_health_check', 
                                    'HealthCheck', 
                                    'NginxRedirect', 
                                    1.0
                                )
    else:
        print("HEAD request returned a non-302 status code: " + str(resp.status_code))
        put_metric_data_wrapper(
                                    cloudwatch, 
                                    'nginx', 
                                    'nginx_redirect_health_check', 
                                    'HealthCheck', 
                                    'NginxRedirect', 
                                    0.0
                                )


def main():
    try:
        whtools_url = os.environ['WHTOOLS_URL']
    except:		
        raise Exception('Missing environment variable: WHTOOLS_URL')
	
    test_nginx_redirect(whtools_url)
	

	
if __name__ == '__main__':
    main()


    
