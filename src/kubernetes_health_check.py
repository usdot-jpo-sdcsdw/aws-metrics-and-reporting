from kubernetes import client, config
import boto3
import sys
import os

"""
Wrapper to call Cloudwatch put metric function
"""
def put_metric_wrapper(cloudwatch, namespace, metric_name, dimension_name, 
    dimension_value, value):
    
    cloudwatch.put_metric_data(
        Namespace=namespace,
        MetricData=[
            {
                'MetricName': metric_name,
                'Dimensions': [
                    {
                        'Name': dimension_name,
                        'Value': dimension_value
                    },
                ],
                'Value': value
            },
        ]
    )
    
"""
Check if variable is None. If it is None, change the value to 0.
This function is used since the Kubernetes API can return metrics
with value None (e.g., status.available_replicas returns None).
None is an invalid value for Cloudwatch metrics and will raise an
error, and therefore the corresponding value of 0 should be recorded 
in Cloudwatch. Valid Cloudwatch metric value types are int, float, 
double, or long.
"""
def none_check(metric):
    if metric is None:
        return 0
    else:
        return metric
    
"""
For each deployment in a deployment list, record metrics in 
Cloudwatch for the number of desired, current, up-to-date, and
available pods. Also record a binary health metric for each 
deployment's status (up or down). Metrics are placed in the
'k8s-metrics' Cloudwatch namespace.
"""
def record_deployment_metrics(cloudwatch, deployment_list):
    for i in deployment_list.items:
        #Deployment name
        name = i.metadata.name
        
        #Number of available pods for the deployment. Value between 0 and n.
        available = none_check(i.status.available_replicas)
        
        #Number of current pods for the deployment. Value between 0 and n.
        current = none_check(i.status.replicas)
        
        #Number of up-to-date pods for the deployment. Value between 0 and n.
        updated = none_check(i.status.updated_replicas)
        
        #Number of desired pods for the deployment. Value between 0 and n.
        desired = none_check(i.spec.replicas)
        
        #Record the number of desired pods for the deployment
        metric_name = create_metric_name(name, '_deployment_desired')
        dimension_value = create_dimension_value(name, 'DeploymentDesired')
        put_metric_wrapper(cloudwatch=cloudwatch, 
            namespace='k8s-metrics', 
            metric_name=metric_name, 
            dimension_name='DeploymentMetric', 
            dimension_value=dimension_value, 
            value=desired)
        
        #Record the number of current pods for the deployment
        metric_name = create_metric_name(name, '_deployment_current')
        dimension_value = create_dimension_value(name, 'DeploymentCurrent')
        put_metric_wrapper(cloudwatch=cloudwatch, 
            namespace='k8s-metrics', 
            metric_name=metric_name, 
            dimension_name='DeploymentMetric', 
            dimension_value=dimension_value, 
            value=current)
        
        #Record the number of up-to-date pods for the deployment
        metric_name = create_metric_name(name, '_deployment_updated')
        dimension_value = create_dimension_value(name, 'DeploymentUpdated')
        put_metric_wrapper(cloudwatch=cloudwatch, 
            namespace='k8s-metrics', 
            metric_name=metric_name, 
            dimension_name='DeploymentMetric', 
            dimension_value=dimension_value, 
            value=updated)
        
        #Record the number of available pods for the deployment
        metric_name = create_metric_name(name, '_deployment_available')
        dimension_value = create_dimension_value(name, 'DeploymentAvailable')
        put_metric_wrapper(cloudwatch=cloudwatch, 
            namespace='k8s-metrics', 
            metric_name=metric_name, 
            dimension_name='DeploymentMetric', 
            dimension_value=dimension_value, 
            value=available)
        
        #Record the health metric: if the number of available pods
        #in the deployment is greater than 0, the deployment is 'up' 
        #and the Cloudwatch metric has a value of 1, otherwise 0.
        metric_name = create_metric_name(name, '_deployment_health_check')
        dimension_value = create_dimension_value(name, 'DeploymentHealthCheck')
        if available > 0:
            put_metric_wrapper(cloudwatch=cloudwatch, 
                namespace='k8s-metrics', 
                metric_name=metric_name, 
                dimension_name='HealthCheck', 
                dimension_value=dimension_value, 
                value=1.0)
        else:
            put_metric_wrapper(cloudwatch=cloudwatch, 
                namespace='k8s-metrics', 
                metric_name=metric_name, 
                dimension_name='HealthCheck', 
                dimension_value=dimension_value, 
                value=0.0)

"""
For each stateful set in a stateful set list, record metrics in Cloudwatch
for the number of desired and current pods. Also record a binary health 
metric for each stateful set's status (up or down). Metrics are placed in the
'k8s-metrics' Cloudwatch namespace.
"""
def record_stateful_set_metrics(cloudwatch, stateful_set_list):
    for i in stateful_set_list.items:
        #Stateful set name
        name = i.metadata.name
        
        #Number of desired pods for the stateful set. Value between 0 and n.
        desired = none_check(i.spec.replicas)
        
        #Number of current pods for the stateful set. Value between 0 and n.
        current = none_check(i.status.current_replicas)
        
        #Record the number of desired pods for the stateful set
        metric_name = create_metric_name(name, '_statefulset_desired')
        dimension_value = create_dimension_value(name, 'StatefulSetDesired')
        put_metric_wrapper(cloudwatch=cloudwatch, 
            namespace='k8s-metrics', 
            metric_name=metric_name, 
            dimension_name='StatefulSetMetric', 
            dimension_value=dimension_value, 
            value=desired)
        
        #Record the number of current pods for the stateful set
        metric_name = create_metric_name(name, '_statefulset_current')
        dimension_value = create_dimension_value(name, 'StatefulSetCurrent')
        put_metric_wrapper(cloudwatch=cloudwatch, 
            namespace='k8s-metrics', 
            metric_name=metric_name, 
            dimension_name='StatefulSetMetric', 
            dimension_value=dimension_value, 
            value=current)
        
        #Record the health metric: if the number of current pods
        #in the stateful set is greater than 0, the stateful set is 'up'
        #and the Cloudwatch metric has a value of 1, otherwise 0.
        metric_name = create_metric_name(name, '_statefulset_health_check')
        dimension_value = create_dimension_value(name, 'StatefulSetHealthCheck')
        if current > 0:
            put_metric_wrapper(cloudwatch=cloudwatch, 
                namespace='k8s-metrics', 
                metric_name=metric_name, 
                dimension_name='HealthCheck', 
                dimension_value=dimension_value, 
                value=1.0)
        else:
            put_metric_wrapper(cloudwatch=cloudwatch, 
                namespace='k8s-metrics', 
                metric_name=metric_name, 
                dimension_name='HealthCheck', 
                dimension_value=dimension_value, 
                value=0.0)
            
"""
Concatenate the name and suffix
"""
def create_metric_name(name, suffix):
    return name + suffix
    
"""
Create a dimension value by capitalizing the first letter of the base name
and then appending the suffix. For instance base=mybase, suffix=MySuffix
results in MybaseMySuffix.
"""
def create_dimension_value(name, suffix):
    return str.upper(name[0]) + name[1:] + suffix
        
def main():
    try:
        kubeconfig = os.environ['KUBECONFIG']
        kubecontext = os.environ['PRODUCTION_KUBECTL_CONTEXT']
        kubernetes_namespace = os.environ['KUBERNETES_NAMESPACE']
    except:
        raise Exception('Missing environment variable: KUBECONFIG, PRODUCTION_KUBECTL_CONTEXT, or KUBERNETES_NAMESPACE')
        
    config.load_kube_config(config_file=kubeconfig, context=kubecontext)
    cloudwatch = boto3.client('cloudwatch')

    #For deployments and stateful sets use
    k8s_api = client.AppsV1beta1Api()

    #Get the list of deployments and stateful sets
    deployment_list = k8s_api.list_namespaced_deployment(namespace=kubernetes_namespace, watch=False)
    stateful_set_list = k8s_api.list_namespaced_stateful_set(namespace=kubernetes_namespace, watch=False)
    
    #Record the metrics in Cloudwatch for each deployment and stateful set
    record_deployment_metrics(cloudwatch, deployment_list)
    record_stateful_set_metrics(cloudwatch, stateful_set_list)

if __name__ == '__main__':
    main()