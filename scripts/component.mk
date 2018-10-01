SHELL=/bin/bash
GET_CREDS="import json, boto3.session as s; \
           print(json.dumps(s.Session().get_credentials().get_frozen_credentials()._asdict()))"

export AWS_REGION=$(shell aws configure get region)
export AWS_ACCOUNT_ID=$(shell aws sts get-caller-identity | jq -r .Account)
export TF_S3_BUCKET=tfstate-$(AWS_ACCOUNT_ID)
export APP_NAME=query-service

default: plan

init:
	terraform init

plan:
	make retrieve-vars
	terraform plan -detailed-exitcode

apply:
	make retrieve-vars
	terraform apply --backup=-

retrieve-vars:
	aws s3 cp s3://org-humancellatlas-861229788715-terraform/query-service/dev/terraform.tfvars terraform.tfvars

upload-vars:
	aws s3 cp terraform.tfvars s3://org-humancellatlas-861229788715-terraform/query-service/dev/terraform.tfvars

get-config:
	@python -c $(GET_CREDS) | jq ".region=env.AWS_REGION | .bucket=env.TF_S3_BUCKET | .key=env.APP_NAME"

init:
	-rm -f .terraform/terraform.tfstate
	terraform init --backend-config <($(MAKE) get-config)

destroy: init
	terraform destroy

clean:
	rm -rf dist .terraform .chalice/deployments

lint:
	flake8 *.py test

test: lint
	python ./test/test.py -v

.PHONY: deploy package init destroy clean lint test