#
# Copyright 2020 Osia authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Module implements dns methods to work with route53 provider"""
import logging

import boto3

from osia.installer.clouds.base import _AbstractInstaller
from osia.installer.dns.base import DNSUtil


def _get_connection(**kwargs):
    return boto3.client('route53', **kwargs)


class Route53Provider(DNSUtil):
    """Class implements DNSUtil base specific for route53"""
    def __init__(self, api_ip=None, apps_ip=None, aws_access_key_id=None, aws_secret_access_key=None, **kwargs):
        super().__init__(**kwargs)

        self.zone_id = None
        self.api_ip = api_ip
        self.apps_ip = apps_ip

        self.boto_kwargs = {
            "aws_access_key_id": aws_access_key_id,
            "aws_secret_access_key": aws_secret_access_key,
        }

    def provider_name(self):
        return 'route53'

    def _get_hosted_zone(self):
        if self.zone_id is None:
            zones = _get_connection(**self.boto_kwargs).list_hosted_zones()['HostedZones']
            result = [v['Id'] for v in zones if v['Name'] == (self.base_domain + ".")]
            if len(result) == 0:
                raise Exception(f"Unable to find hosted_zone {self.base_domain} in zone list.")
            self.zone_id = result[0]
        return self.zone_id

    def _execute_command(self, prefix: str, mode: str, ip_addr: str):
        change_batch = {
            'Changes': [
                {'Action': mode,
                 'ResourceRecordSet': {
                     'Name': '.'.join([prefix, self.cluster_name, self.base_domain]) + '.',
                     'Type': 'A',
                     'TTL': self.ttl,
                     'ResourceRecords': [
                         {'Value': ip_addr}
                     ]
                 }
                 }
            ]
        }
        conn = _get_connection(**self.boto_kwargs)
        try:
            conn.change_resource_record_sets(
                HostedZoneId=self._get_hosted_zone(),
                ChangeBatch=change_batch)
        except conn.exceptions.InvalidChangeBatch as ex:
            logging.warning("Exception thrown while %s operation, next steps will possibly fail",
                            mode.lower())
            logging.debug(ex)
        self.modified = True

    def add_api_domain(self, instance: _AbstractInstaller):
        self.api_ip = instance.get_api_ip()
        self._execute_command('api', 'CREATE', self.api_ip)

    def add_apps_domain(self, instance: _AbstractInstaller):
        self.apps_ip = instance.get_apps_ip()
        self._execute_command('*.apps', 'CREATE', self.apps_ip)

    def delete_domains(self):
        if self.api_ip is not None:
            self._execute_command('api', 'DELETE', self.api_ip)
        if self.apps_ip is not None:
            self._execute_command('*.apps', 'DELETE', self.apps_ip)
        self.delete_file()
