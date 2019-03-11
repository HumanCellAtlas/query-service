SHELL=/bin/bash -o pipefail

ifndef APP_NAME
$(error Please run "source environment" in the repo root directory before running make commands)
endif

SAM_TX="import sys, json, boto3, samtranslator.translator.transform as t, samtranslator.public.translator as pt; \
        print(json.dumps(t.transform(json.load(sys.stdin), {}, pt.ManagedPolicyLoader(boto3.client('iam')))))"
GET_CREDS="import json, boto3.session as s; \
           print(json.dumps(s.Session().get_credentials().get_frozen_credentials()._asdict()))"

WEBHOOK_SECRET_NAME=$(APP_NAME)/$(STAGE)/webhook-auth-config

deploy: init-tf package
	$(eval LAMBDA_MD5 = $(shell md5sum dist/deployment.zip | cut -f 1 -d ' '))
	aws s3 cp dist/deployment.zip s3://$(TF_S3_BUCKET)/$(LAMBDA_MD5).zip
	cat dist/sam.json | \
         jq '.Outputs.BundleEventHandlerName.Value.Ref="BundleEventHandler"' | \
         jq '.Outputs.AsyncQueryHandlerName.Value.Ref="AsyncQueryHandler"' | \
         jq '.Resources.APIHandler.Properties.CodeUri="s3://$(TF_S3_BUCKET)/$(LAMBDA_MD5).zip"' | \
         jq '.Resources.BundleEventHandler.Properties.CodeUri="s3://$(TF_S3_BUCKET)/$(LAMBDA_MD5).zip"' | \
         jq '.Resources.AsyncQueryHandler.Properties.CodeUri="s3://$(TF_S3_BUCKET)/$(LAMBDA_MD5).zip"' | \
         python -c $(SAM_TX) > dist/cloudformation.json
	terraform apply
	$(MAKE) $(TFSTATE_FILE)
	$(MAKE) install-webhooks
	$(MAKE) get-tf-output | jq -r .rds_cluster_endpoint.value | aegea secrets put $(APP_NAME)/$(STAGE)/db/hostname
	$(MAKE) get-tf-output | jq -r .rds_cluster_readonly_endpoint.value | aegea secrets put $(APP_NAME)/$(STAGE)/db/readonly_hostname
	$(MAKE) get-tf-output

$(TFSTATE_FILE):
	terraform state pull > $(TFSTATE_FILE)

init-secrets:
	python -c "import secrets; print(secrets.token_urlsafe(32))" > secrets/db_password
	export SECRET=$$(python -c "import secrets; print(secrets.token_urlsafe(32))"); \
	 cat secrets/webhook_template.json | envsubst > secrets/webhook.json

install-webhooks:
	FUNCTION_NAME=$$($(MAKE) get-tf-output | jq -r .api_handler_name.value); \
	 APIHANDLER_IAM_ROLE=$$(aws lambda get-function --function-name $$FUNCTION_NAME | jq -r .Configuration.Role | cut -d / -f 2); \
	 cat secrets/webhook.json | aegea secrets put $(WEBHOOK_SECRET_NAME) --iam-role $$APIHANDLER_IAM_ROLE
	python -m $(APP_NAME).webhooks install --callback-url=$$($(MAKE) get-tf-output | jq -r .api_endpoint_url.value)bundles/event

install-secrets:
	echo -n $(APP_NAME) | aegea secrets put $(APP_NAME)/$(STAGE)/db/username
	cat secrets/db_password | aegea secrets put $(APP_NAME)/$(STAGE)/db/password

package:
	rm -rf vendor
	mkdir vendor
	cp -a $(APP_NAME) $(APP_NAME)-api.yml vendor
	shopt -s nullglob; for wheel in vendor.in/*/*.whl; do unzip -q -o -d vendor $$wheel; done
	cat iam/policy-templates/$(APP_NAME)-lambda.json | envsubst > .chalice/policy-$(STAGE).json
	cd .chalice; jq .app_name=env.APP_NAME config.json | sponge config.json
	cd .chalice; for var in $$EXPORT_ENV_VARS_TO_LAMBDA; do \
            jq .stages.$(STAGE).environment_variables.$$var=env.$$var config.json | sponge config.json; \
        done
	chalice package --stage $(STAGE) dist

get-config:
	@python -c $(GET_CREDS) | jq ".region=env.AWS_DEFAULT_REGION | .bucket=env.TF_S3_BUCKET | .key=env.APP_NAME"

get-tf-output:
	@terraform output -module=$(APP_NAME) -json

init-tf:
	-rm -f .terraform/*.tfstate
	$(MAKE) get-config > .terraform/aws_config
	terraform init

destroy: init-tf
	terraform destroy

clean:
	git clean -Xdf dist .terraform .chalice

lint:
	flake8 *.py $(APP_NAME) test
	mypy $(APP_NAME) --ignore-missing-imports

test: lint
	coverage run -m unittest discover --start-directory test --top-level-directory . --verbose

fetch:
	scripts/fetch.py

init-db:
	python -m $(APP_NAME).db init

load: init-db
	python -m $(APP_NAME).db load

load-test-data: init-db
	python -m $(APP_NAME).db load-test

update: $(TFSTATE_FILE)
	zip -r dist/deployment.zip app.py $(APP_NAME) $(APP_NAME)-api.yml
	$(MAKE) get-tf-output | jq -r '.|values[].value' | egrep "^$(APP_NAME)-.+Handler-" | \
	 xargs -n 1 -P 8 -I % aws lambda update-function-code --function-name % --zip-file fileb://dist/deployment.zip

get-logs:
	aws logs describe-log-groups --log-group-name-prefix /aws/lambda/$(APP_NAME)- | \
	 jq -r .logGroups[].logGroupName | \
	 xargs -n 1 aegea logs --start-time=-5m

refresh_all_requirements:
	@echo -n '' >| requirements.txt
	@echo -n '' >| requirements-dev.txt
	@if [ $$(uname -s) == "Darwin" ]; then sleep 1; fi  # this is require because Darwin HFS+ only has second-resolution for timestamps.
	@touch requirements.txt.in requirements-dev.txt.in
	@$(MAKE) requirements.txt requirements-dev.txt

requirements.txt requirements-dev.txt : %.txt : %.txt.in
	[ ! -e .requirements-env ] || exit 1
	virtualenv -p $(shell which python3) .$<-env
	.$<-env/bin/pip install -r $@
	.$<-env/bin/pip install -r $<
	echo "# You should not edit this file directly.  Instead, you should edit $<." >| $@
	.$<-env/bin/pip freeze >> $@
	rm -rf .$<-env

requirements-dev.txt : requirements.txt.in

.PHONY: deploy package init-tf init-db destroy clean lint test
