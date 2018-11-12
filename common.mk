SHELL=/bin/bash
GET_CREDS="import json, boto3.session as s; \
           print(json.dumps(s.Session().get_credentials().get_frozen_credentials()._asdict()))"

export AWS_REGION=$(shell aws configure get region)
export AWS_ACCOUNT_ID=$(shell aws sts get-caller-identity | jq -r .Account)
export TF_S3_BUCKET=org-humancellatlas-$(AWS_ACCOUNT_ID)-terraform
export APP_NAME=query-service


default: plan

secrets:
	aws secretsmanager get-secret-value \
		--secret-id query/$(DEPLOYMENT_STAGE)/config.json | \
		jq -r .SecretString | \
		python -m json.tool > terraform/terraform.tfvars


plan:
	terraform plan -detailed-exitcode

apply:
	terraform apply --backup=-

init:
	-rm -f .terraform/terraform.tfstate
	terraform init \
		-backend-config="bucket=${TF_S3_BUCKET}" \
		-backend-config="key=query-service/$(DEPLOYMENT_STAGE)/terraform.tfstate" \
		-backend-config="profile=${AWS_PROFILE}" \
		-backend-config="region=${AWS_REGION}"

destroy: init
	terraform destroy

clean:
	rm -rf dist .terraform .chalice/deployments

lint:
	flake8 *.py test

test: lint
	python ./test/test.py -v

.PHONY: deploy package init destroy clean lint test secrets
