# AWS Metrics and Reporting

This repository contains:
* (1) scripts to perform health checks on system resources and record metrics in Amazon Cloudwatch
* (2) scripts to access the Amazon Cloudwatch metrics and perform uptime calculations for each resource

### Prerequisites
* Python: https://www.python.org/downloads/
    * Development and testing performed on version 2.7.12: https://www.python.org/downloads/release/python-2712/
* Additional Python packages (recommended installation via pip):
    * boto3: https://boto3.amazonaws.com/v1/documentation/api/latest/index.html
    * kubernetes: https://github.com/kubernetes-client/python
* Git: https://git-scm.com/

### Getting Started

#### Step 1 - Clone this repository
```
git clone https://github.com/usdot-jpo-sdcsdw/aws-metrics-and-reporting.git
```
#### Step 2 - Setup
*Some scripts require setting certain environment variables to run. These variables include:*
* KUBECONFIG - Path to the Kubernetes configuration file
* KUBERNETES_NAMESPACE - The namespace for the Kubernetes cluster
* PRODUCTION_KUBECTL_CONTEXT - The production context for the Kubernetes cluster
* TOPIC_ARN - The Amazon Resource Number for the SNS topic used for reporting
* HEALTH_CHECK_FREQUENCY - The frequency of resource health checks in seconds. For instance, 60.0 is the value for once a minute.
* WHTOOLS_URL - The URL endpoint for performing the NGINX health check
* QUERY_URL - The URL endpoint for a REST query
* USERNAME - Username required for a REST query
* PASSWORD - Password required for a REST query

AWS credentials must be configured to access Cloudwatch. Please see the *[Quickstart - Configuration](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html#configuration)* section in the boto3 documentation for details.
#### Step 3 - Run the scripts
```
cd aws-metrics-and-reporting
python <script>
```

## License

This project is licensed under the Apache License - see  [LICENSE](LICENSE) file for details