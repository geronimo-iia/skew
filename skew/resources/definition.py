# Copyright (c) 2014 Scopely, Inc.
# Copyright (c) 2015 Mitch Garnaat
# Copyright (c) 2020 Jerome Guibert
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

import importlib
from typing import Dict, List

__all__ = ["all_providers", "all_services", "all_types", "find_resource_class"]


# Maps resources names as they appear in ARN's to the path name
# of the Python class representing that resource.
_RESOURCE_TYPES: Dict[str, str] = {
    "aws.acm.certificate": "aws.acm.Certificate",
    "aws.apigateway.restapis": "aws.apigateway.RestAPI",
    "aws.autoscaling.autoScalingGroup": "aws.autoscaling.AutoScalingGroup",
    "aws.autoscaling.launchConfigurationName": "aws.autoscaling.LaunchConfiguration",
    "aws.cloudfront.distribution": "aws.cloudfront.Distribution",
    "aws.cloudformation.stack": "aws.cloudformation.Stack",
    "aws.cloudsearch.domain": "aws.cloudsearch.Domain",
    "aws.cloudwatch.alarm": "aws.cloudwatch.Alarm",
    "aws.logs.log-group": "aws.cloudwatch.LogGroup",
    "aws.cloudtrail.trail": "aws.cloudtrail.CloudTrail",
    "aws.dynamodb.table": "aws.dynamodb.Table",
    "aws.ec2.address": "aws.ec2.Address",
    "aws.ec2.customer-gateway": "aws.ec2.CustomerGateway",
    "aws.ec2.key-pair": "aws.ec2.KeyPair",
    "aws.ec2.image": "aws.ec2.Image",
    "aws.ec2.instance": "aws.ec2.Instance",
    "aws.ec2.natgateway": "aws.ec2.NatGateway",
    "aws.ec2.network-acl": "aws.ec2.NetworkAcl",
    "aws.ec2.route-table": "aws.ec2.RouteTable",
    "aws.ec2.internet-gateway": "aws.ec2.InternetGateway",
    "aws.ec2.security-group": "aws.ec2.SecurityGroup",
    "aws.ec2.snapshot": "aws.ec2.Snapshot",
    "aws.ec2.volume": "aws.ec2.Volume",
    "aws.ec2.vpc": "aws.ec2.Vpc",
    "aws.ec2.flow-log": "aws.ec2.FlowLog",
    "aws.ec2.vpc-peering-connection": "aws.ec2.VpcPeeringConnection",
    "aws.ec2.subnet": "aws.ec2.Subnet",
    "aws.ec2.launch-template": "aws.ec2.LaunchTemplate",
    "aws.ecs.cluster": "aws.ecs.Cluster",
    "aws.ecs.task-definition": "aws.ecs.TaskDefinition",
    "aws.ecr.registery": "aws.ecr.Registery",
    "aws.ecr.repository": "aws.ecr.Repository",
    "aws.efs.filesystem": "aws.efs.Filesystem",
    "aws.elasticache.cluster": "aws.elasticache.Cluster",
    "aws.elasticache.subnet-group": "aws.elasticache.SubnetGroup",
    "aws.elasticache.snapshot": "aws.elasticache.Snapshot",
    "aws.elasticbeanstalk.application": "aws.elasticbeanstalk.Application",
    "aws.elasticbeanstalk.environment": "aws.elasticbeanstalk.Environment",
    "aws.elb.loadbalancer": "aws.elb.LoadBalancer",
    "aws.elbv2.loadbalancer": "aws.elbv2.LoadBalancer",
    "aws.elbv2.targetgroup": "aws.elbv2.TargetGroup",
    "aws.es.domain": "aws.es.ElasticsearchDomain",
    "aws.events.rule": "aws.cloudwatch.CloudWatchEventRule",
    "aws.firehose.deliverystream": "aws.firehose.DeliveryStream",
    "aws.iam.group": "aws.iam.Group",
    "aws.iam.instance-profile": "aws.iam.InstanceProfile",
    "aws.iam.role": "aws.iam.Role",
    "aws.iam.policy": "aws.iam.Policy",
    "aws.iam.user": "aws.iam.User",
    "aws.iam.server-certificate": "aws.iam.ServerCertificate",
    "aws.kinesis.stream": "aws.kinesis.Stream",
    "aws.kms.key": "aws.kms.Key",
    "aws.lambda.function": "aws.lambda.Function",
    "aws.opsworks.stack": "aws.opsworks.Stack",
    "aws.rds.db": "aws.rds.DBInstance",
    "aws.rds.secgrp": "aws.rds.DBSecurityGroup",
    "aws.redshift.cluster": "aws.redshift.Cluster",
    "aws.route53.hostedzone": "aws.route53.HostedZone",
    "aws.route53.healthcheck": "aws.route53.HealthCheck",
    "aws.s3.bucket": "aws.s3.Bucket",
    "aws.states.statemachine": "aws.states.StateMachines",
    "aws.sqs.queue": "aws.sqs.Queue",
    "aws.ses.identity": "aws.ses.Identity",
    "aws.sns.subscription": "aws.sns.Subscription",
    "aws.sns.topic": "aws.sns.Topic",
    "aws.support.check": "aws.support.Check",
}


def all_providers():
    """Return all providers defined in resource types."""
    providers = set()
    for resource_type in _RESOURCE_TYPES:
        providers.add(resource_type.split(".")[0])
    return list(providers)


def all_services(provider_name: str) -> List[str]:
    """Return all services defined in resource types."""
    services = set()
    for resource_type in _RESOURCE_TYPES:
        t = resource_type.split(".")
        if t[0] == provider_name:
            services.add(t[1])
    return list(services)


def all_types(provider_name: str, service_name: str) -> List[str]:
    """Return all types defined in resource types."""
    types = set()
    for resource_type in _RESOURCE_TYPES:
        t = resource_type.split(".")
        if t[0] == provider_name and t[1] == service_name:
            types.add(t[2])
    return list(types)


def find_resource_class(resource_path):
    """Dynamically load a class from a string."""
    class_path = _RESOURCE_TYPES[resource_path]
    class_data = f"skew.resources.{class_path}".split(".")
    module_path = ".".join(class_data[:-1])
    class_str = class_data[-1]
    module = importlib.import_module(module_path)
    # Finally, we retrieve the Class
    return getattr(module, class_str)
