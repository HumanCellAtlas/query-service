#!/usr/bin/env python

# This utility script runs the equivalent of `chalice package --pkg-format terraform`, but without building the
# distribution zipfile. It is used by `make lint` to help lint the Terraform configuration.

import os
from chalice.deploy.packager import LambdaDeploymentPackager
from chalice.package import TerraformCodeLocationPostProcessor
from chalice.cli.factory import CLIFactory

LambdaDeploymentPackager.create_deployment_package = lambda *args, **kwargs: "lint.tf"
TerraformCodeLocationPostProcessor.process = lambda *args, **kwargs: None

factory = CLIFactory(os.environ["APP_HOME"])
config = factory.create_config_obj(os.environ["STAGE"])
packager = factory.create_app_packager(config, "terraform")
packager.package_app(config, "terraform", os.environ["STAGE"])
