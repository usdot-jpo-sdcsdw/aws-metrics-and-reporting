import boto3
import datetime
import sys
import os

"""
Calculate the start time to be one month before the end time.
Assumes the end time day will be valid for the previous month.
For instance, end time may be the first of the month, but
not the end of the month (e.g., not all months have 31 days).
"""
def calc_start_time(end_time):
    if end_time.month == 1:
        return end_time.replace(month=12, year=(end_time.year-1))
    else:
        return end_time.replace(month=(end_time.month-1))

"""
Wrapper to call Cloudwatch get metric statistics function. The only
statistic retrieved is the sum of the metrics.

The function returns a dictionary with a list 'Datapoints'. Each datapoint
aggregates the statistics for one period. For instance, if the period is 
3600 (one hour), the metric statistics for that hour will be recorded in 
a single data point.
"""
def get_metric_stats_wrapper(cloudwatch, namespace, metric_name, 
    dimension_name, dimension_value, period, start_time, end_time):
    
    stats = cloudwatch.get_metric_statistics(
        Namespace=namespace,
        MetricName=metric_name,
        Dimensions=[
            {
                'Name': dimension_name,
                'Value': dimension_value
            },
        ],
        StartTime=start_time,
        EndTime=end_time,
        Period=period,
        Statistics=[
            'Sum',
        ],
    )
    
    return stats

"""
Given a start time, an end time, a list of Cloudwatch metric statistics,
and the frequency of checks in seconds, calculate the uptime. 
This function assumes that the health metric of a resource is recorded with 
value 1 for 'up', and value 0 for 'down'. The uptime is calculated by 
summing the total number of checks reporting 'up' and dividing by the total 
number of checks.
"""
def calc_uptime(stats, start_time, end_time, frequency):
    total_up = 0.0
    total_possible = (end_time-start_time).total_seconds()/frequency   #1 check / x seconds
    
    for point in stats['Datapoints']:
        total_up += point['Sum']
        
    return 100 * total_up / total_possible
    
def send_uptime_report(message, topic):
    sns = boto3.client('sns')

    response = sns.publish(
        TopicArn=topic,
        Subject='SDC/SDW Uptime Report',
        Message=message
    )

def main():
    try:
        topic = os.environ['TOPIC_ARN']
        frequency = float(os.environ['HEALTH_CHECK_FREQUENCY'])
    except:
        raise Exception('Missing environment variable: TOPIC_ARN or HEALTH_CHECK_FREQUENCY')

    cloudwatch = boto3.client('cloudwatch')

    #Get the start time and end times for the metric collection time range
    end_time=datetime.datetime.utcnow()
    start_time = calc_start_time(end_time)
    
    #Specifies the period used when calling Cloudwatch to get metric statistics.
    #Note that 3600 is not a mandatory number, but does comply with Cloudwatch
    #recommendations as the most general value. Per the documentation, the 
    #period should comply with:
    #Start time between 3 hours and 15 days ago - use a multiple of 60 seconds
    #Start time between 15 and 63 days ago - use a multiple of 300 seconds
    #Start time between greater than 63 days ago - use a multiple of 3600 seconds
    period=3600
    
    #Start credentials db uptime
    stats = get_metric_stats_wrapper(cloudwatch=cloudwatch, 
        namespace='k8s-metrics', 
        metric_name='credentials-db_statefulset_health_check', 
        dimension_name='HealthCheck', 
        dimension_value='Credentials-dbStatefulSetHealthCheck', 
        period=period, 
        start_time=start_time, 
        end_time=end_time)
        
    cred_db_uptime = calc_uptime(stats, start_time, end_time, frequency)
    #End credentials db uptime

    #Start tim db uptime
    stats = get_metric_stats_wrapper(cloudwatch=cloudwatch, 
        namespace='k8s-metrics', 
        metric_name='tim-db_statefulset_health_check', 
        dimension_name='HealthCheck', 
        dimension_value='Tim-dbStatefulSetHealthCheck', 
        period=period, 
        start_time=start_time, 
        end_time=end_time)
        
    tim_db_uptime = calc_uptime(stats, start_time, end_time, frequency)
    #End tim db uptime

    #Start message validator uptime
    stats = get_metric_stats_wrapper(cloudwatch=cloudwatch, 
        namespace='k8s-metrics', 
        metric_name='message-validator_deployment_health_check', 
        dimension_name='HealthCheck', 
        dimension_value='Message-validatorDeploymentHealthCheck', 
        period=period, 
        start_time=start_time, 
        end_time=end_time)
        
    message_validator_uptime = calc_uptime(stats, start_time, end_time, frequency)
    #End message validator uptime

    #Start whtools uptime
    stats = get_metric_stats_wrapper(cloudwatch=cloudwatch, 
        namespace='k8s-metrics', 
        metric_name='whtools_deployment_health_check', 
        dimension_name='HealthCheck', 
        dimension_value='WhtoolsDeploymentHealthCheck', 
        period=period, 
        start_time=start_time, 
        end_time=end_time)
        
    whtools_uptime = calc_uptime(stats, start_time, end_time, frequency)
    #End whtools uptime

    #Start cas uptime
    stats = get_metric_stats_wrapper(cloudwatch=cloudwatch, 
        namespace='k8s-metrics', 
        metric_name='cas_deployment_health_check', 
        dimension_name='HealthCheck', 
        dimension_value='CasDeploymentHealthCheck', 
        period=period, 
        start_time=start_time, 
        end_time=end_time)
        
    cas_uptime = calc_uptime(stats, start_time, end_time, frequency)
    #End cas uptime

    #Start Nginx uptime
    stats = get_metric_stats_wrapper(cloudwatch=cloudwatch, 
        namespace='nginx', 
        metric_name='nginx_redirect_health_check', 
        dimension_name='HealthCheck', 
        dimension_value='NginxRedirect', 
        period=period, 
        start_time=start_time, 
        end_time=end_time)
        
    nginx_uptime = calc_uptime(stats, start_time, end_time, frequency)
    #End Nginx uptime

    #Start REST query uptime
    stats = get_metric_stats_wrapper(cloudwatch=cloudwatch, 
        namespace='query-endpoint', 
        metric_name='query_endpoint_check', 
        dimension_name='HealthCheck', 
        dimension_value='QueryEndpoint', 
        period=period, 
        start_time=start_time, 
        end_time=end_time)
        
    query_uptime = calc_uptime(stats, start_time, end_time, frequency)
    #End REST query uptime
    
    #Format start and end times for message
    start_time_str=start_time.strftime("%Y-%m-%d %H:%M:%S")
    end_time_str=end_time.strftime("%Y-%m-%d %H:%M:%S")
    message=("The uptime report is calculated as follows:\n\nSystem resource "
        "statuses are obtained every minute. For Kubernetes, statuses are obtained "
        "for each deployment and stateful set in the cluster. If a deployment or "
        "stateful set has at least one available pod, a metric is recorded in "
        "Cloudwatch with value 1, otherwise with a value of 0. Metrics are "
        "similarly recorded in Cloudwatch for the statuses of NGINX and the REST "
        "query endpoint. The NGINX metric represents successful redirection from "
        "webapp.cvmvp.com to the CAS server; the REST query endpoint checks for "
        "successful query responses.\n\nOnce a month, the uptime for each resource "
        "is calculated as a percentage of the number of successful health checks to "
        "the total number of health checks.\n\n*****UPTIME FOR {} --- {}*****\n\n"
        "\n\tCREDENTIALS-DB STATEFULSET: {}\n\tTIM-DB STATEFULSET: {}\n\tMESSAGE-VALIDATOR "
        "DEPLOYMENT: {}\n\tWHTOOLS DEPLOYMENT: {}\n\tCAS DEPLOYMENT: {}\n\tNGINX REDIRECT "
        "UPTIME: {}\n\tREST QUERY ENDPOINT: {}\n\n").format(start_time_str, end_time_str, 
        cred_db_uptime, tim_db_uptime, message_validator_uptime, whtools_uptime, 
        cas_uptime, nginx_uptime, query_uptime)
    
    #Send the uptime report
    send_uptime_report(message, topic)

if __name__ == '__main__':
    main()