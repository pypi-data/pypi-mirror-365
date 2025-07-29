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
"""Module implements common base for install-config
creation.
It also implements logic to obtain correct specification
for specified installation platform"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from subprocess import run
from typing import Protocol

from jinja2 import Environment, PackageLoader
from semantic_version import (SimpleSpec,  # type: ignore[import-untyped]
                              Version)


class AbstractInstaller(ABC):
    """Base object for configuration of install-config"""
    # pylint: disable=too-many-instance-attributes

    __env: Environment | None = None

    # pylint: disable=too-many-arguments
    def __init__(self,
                 cluster_name=None,
                 base_domain=None,
                 master_flavor=None,
                 master_replicas='3',
                 pull_secret_file=None,
                 ssh_key_file=None,
                 worker_flavor=None,
                 worker_replicas='3',
                 certificate_bundle_file=None,
                 cluster_directory=None,
                 skip_clean=False,
                 enable_fips=False,
                 installer=None,
                 **unused_kwargs):
        self.cluster_name = cluster_name
        self.base_domain = base_domain
        self.master_flavor = master_flavor
        self.master_replicas = master_replicas
        self.pull_secret_file = pull_secret_file
        self.pull_secret = None
        self.ssh_key_file = ssh_key_file
        self.ssh_key = None
        self.certificate_bundle_file = certificate_bundle_file
        self.certificate_bundle = None
        self.worker_flavor = worker_flavor
        self.worker_replicas = worker_replicas
        self.cluster_directory = cluster_directory
        self.skip_clean = skip_clean
        self.installer = installer
        self.enable_fips = enable_fips
        self.ocp_version = None
        self.network_type = "OVNKubernetes"

    @abstractmethod
    def acquire_resources(self):
        """Method which is called before the install-config can be generated.
        The method should be used to get all necessary dependencies to fill
        in details in install-config"""

    @abstractmethod
    def get_template_name(self):
        """Method to obtain name of jinja template related to specified platform."""

    @abstractmethod
    def post_installation(self):
        """Method called after the installation is done, this is the place where,
        things like registration of apps domain and other is expected to happen."""

    @abstractmethod
    def get_api_ip(self) -> str | None:
        """Returns api ip address if dns is supported, None otherwise.
        """

    @abstractmethod
    def get_apps_ip(self):
        """Returns apps ip if dns is supported, None otherwise
        """

    def _resolve_version(self):
        if self.ocp_version is None:
            capture = run([self.installer, "version"], capture_output=True, check=False)
            ver_string = capture.stdout.decode("utf-8").splitlines()[0].split(' ')[1]
            self.ocp_version = ver_string
            logging.info("Resolved installed version as %s", self.ocp_version)

    def _resolve_network_type(self):
        self._resolve_version()
        ver = Version(self.ocp_version)
        spec = SimpleSpec('<4.15')
        if ver in spec:
            logging.debug("Older version of openshift, falling back to OpenShiftSDN")
            self.network_type = 'OpenShiftSDN'

    def check_clean(self):
        """Method returns if installation is configured to clean resources
        on failure."""
        return not self.skip_clean

    def process_template(self):
        """Method executes creation of install-config.yaml"""
        self._resolve_network_type()
        with open(self.pull_secret_file) as ps_file:
            self.pull_secret = ps_file.read()
        with open(self.ssh_key_file) as key_file:
            self.ssh_key = key_file.read()
        if self.certificate_bundle_file is not None:
            with open(self.certificate_bundle_file) as cert_file:
                self.certificate_bundle = cert_file.read()
        template = AbstractInstaller.get_environment().get_template(self.get_template_name())
        result = template.render(self.__dict__)
        with open(f"{self.cluster_name}/install-config.yaml", "w") as yaml_file:
            yaml_file.write(result)

    @classmethod
    def get_environment(cls) -> Environment:
        """Method loads jinja templates"""
        if cls.__env is None:
            cls.__env = Environment(loader=PackageLoader("osia.installer"))
        return cls.__env


class _AbstractInstaller(Protocol):
    """Base object for configuration of install-config"""
    __env: Environment | None

    # pylint: disable=too-many-arguments
    def __init__(self,
                 cluster_name=None,
                 base_domain=None,
                 master_flavor=None,
                 master_replicas='3',
                 pull_secret_file=None,
                 ssh_key_file=None,
                 worker_flavor=None,
                 worker_replicas='3',
                 certificate_bundle_file=None,
                 cluster_directory=None,
                 skip_clean=False,
                 enable_fips=False,
                 installer=None,
                 **unused_kwargs): ...

    @abstractmethod
    def acquire_resources(self):
        """Method which is called before the install-config can be generated.
        The method should be used to get all necessary dependencies to fill
        in details in install-config"""

    @abstractmethod
    def get_template_name(self):
        """Method to obtain name of jinja template related to specified platform."""

    @abstractmethod
    def post_installation(self):
        """Method called after the installation is done, this is the place where,
        things like registration of apps domain and other is expected to happen."""

    @abstractmethod
    def get_api_ip(self) -> str | None:
        """Returns api ip address if dns is supported, None otherwise.
        """

    @abstractmethod
    def get_apps_ip(self):
        """Returns apps ip if dns is supported, None otherwise
        """

    def _resolve_version(self): ...

    def _resolve_network_type(self): ...

    def check_clean(self):
        """Method returns if installation is configured to clean resources
        on failure."""

    def process_template(self):
        """Method executes creation of install-config.yaml"""

    @classmethod
    def get_environment(cls) -> Environment:
        """Method loads jinja templates"""


class InstallerProvider:
    """Class implements dynamic provider of registered platform specific
    implementations of AbstractInstaller.
    Class implements singleton design pattern."""
    __instance: InstallerProvider | None = None

    @classmethod
    def instance(cls) -> InstallerProvider:
        """Method to obtains singleton instance."""
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    @classmethod
    def register(cls, name, instance):
        """Method to dynamically register implementation of AbstractInstaller"""
        cls.instance().add_installer(name, instance)

    def __init__(self):
        self.installers: dict[str, type[_AbstractInstaller]] = {}

    def add_installer(self, name: str, instance: type[_AbstractInstaller]):
        """Insert concrete implementation of AbstractInstaller into the registry"""
        self.installers[name] = instance

    def __getitem__(self, name: str) -> type[_AbstractInstaller]:
        return self.installers[name]
