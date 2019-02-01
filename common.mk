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
		python -m json.tool > $(PROJECT_ROOT)/terraform/terraform.tfvars


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

gitlab-init:
	-rm -f .terraform/terraform.tfstate
	terraform init \
		-backend-config="bucket=${TF_S3_BUCKET}" \
		-backend-config="key=query-service/$(DEPLOYMENT_STAGE)/terraform.tfstate"

destroy: init
	terraform destroy

clean:
	rm -rf dist .terraform .chalice/deployments

lint:
	flake8 *.py test

test: lint
	python ./test/test.py -v

.PHONY: deploy package init destroy clean lint test secrets install build stage

install:
	virtualenv -p python3 venv
	. venv/bin/activate && pip install -r requirements.txt --upgrade

build:
	rm -rf target
	rm -rf load_data.zip
	mkdir target
	mkdir target/query
	pip install -r requirements.txt -t target/ --upgrade

	cp -R vendor.in/* target/

	rsync -av ../query target/ --exclude venv/ --exclude test/

	cp -R *.py target/
	# psycopg2.zip contains the psycopg2-3.6 package downloaded from https://github.com/jkehler/awslambda-psycopg2
	# and renamed psycopg2
	unzip $(PROJECT_ROOT)/psycopg2.zip
	cp -R build/ target/
	rm -rf build
	shopt -s nullglob; for wheel in vendor.in/*/*.whl; do unzip -q -o -d vendor $$wheel; done

	cp -R vendor/* target/

	cd target && zip -r ../$(ZIP_FILE) *

stage: build
	aws s3 cp $(ZIP_FILE) s3://$(BUCKET)/$(STAGED_FILE_KEY)