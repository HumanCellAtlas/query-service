SHELL=/bin/bash -o pipefail

ifndef APP_NAME
$(error Please run "source environment" in the repo root directory before running make commands)
endif

deploy: init-tf package
	$(eval export LAMBDA_SHA = $(shell sha256sum dist/deployment.zip | cut -f 1 -d ' ' | base64 --wrap=0))
	aws s3 cp dist/deployment.zip s3://$(TF_S3_BUCKET)/$(LAMBDA_SHA).zip
	jq -f scripts/preprocess_chalice_tf_config.jq dist/chalice.tf.json > terraform/chalice.tf.json
	terraform apply
	$(MAKE) $(TFSTATE_FILE)
	$(MAKE) install-webhooks
	terraform output $(APP_NAME)
	$(MAKE) get-status

get-status:
	http --check-status GET https://$(API_DOMAIN_NAME)/internal/health

$(TFSTATE_FILE):
	terraform state pull > $(TFSTATE_FILE)

install-webhooks:
	python -m $(APP_NAME).webhooks install --callback-url=$$(terraform output --json $(APP_NAME) | jq -r .EndpointURL)bundles/event

install-secrets:
	aws secretsmanager put-secret-value --secret-id $(APP_NAME)/$(STAGE)/postgresql/password --secret-string $$(python -c 'import secrets; print(secrets.token_urlsafe(32))')
	aws rds modify-db-cluster --db-cluster-identifier $$(terraform output --json $(APP_NAME) | jq -r .rds_cluster_id) --master-user-password $$(aws secretsmanager get-secret-value --secret-id $(APP_NAME)/$(STAGE)/postgresql/password | jq -r .SecretString) --apply-immediately

build-chalice-config:
	envsubst < iam/policy-templates/$(APP_NAME)-lambda.json > .chalice/policy-$(STAGE).json
	cd .chalice; jq .app_name=env.APP_NAME < config.in.json > config.json
	cd .chalice; for var in $$EXPORT_ENV_VARS_TO_LAMBDA; do \
            jq .stages.$(STAGE).environment_variables.$$var=env.$$var config.json | sponge config.json; \
        done
	cd .chalice; V=$$(git describe --tags --always) jq .stages.$(STAGE).environment_variables.VERSION=env.V config.json | sponge config.json
	cd .chalice; jq .stages.$(STAGE).tags.env=env.STAGE config.json | sponge config.json
	cd .chalice; jq .stages.$(STAGE).tags.service=env.APP_NAME config.json | sponge config.json
	cd .chalice; jq .stages.$(STAGE).tags.owner=env.OWNER config.json | sponge config.json
	cd .chalice; jq .stages.$(STAGE).api_gateway_stage=env.STAGE config.json | sponge config.json

# package prepares a Lambda zipfile with the help of the Chalice packager (which also emits a SAM template).
# We also inject any wheels found in vendor.in, and rewrite the zipfile to make the build reproducible.
package: build-chalice-config
	rm -rf vendor dist/deployment
	mkdir vendor
	cp -a $(APP_NAME) $(APP_NAME)-api.yml vendor
	find vendor -name '*.pyc' -delete
	find vendor -exec touch -t 201901010000 {} \; # Reset mtimes on all vendor files to make zipfile contents reproducible
	shopt -s nullglob; for wheel in vendor.in/*/*.whl; do pip install --target vendor --upgrade $$wheel; done
	chalice package --pkg-format terraform --stage $(STAGE) dist
	cd dist; mkdir deployment; cd deployment; unzip -q -o ../deployment.zip
	$(MAKE) prune
	find dist/deployment -exec touch -t 201901010000 {} \; # Reset mtimes on all dep files to make zipfile contents reproducible
	rm dist/deployment.zip
	cd dist/deployment; zip -q -X -r ../deployment.zip .

# Remove unused dependencies that consume substantial space in the package.
# See https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtimes.html
prune:
	cd dist/deployment; rm -rf awscli* boto3* botocore* cryptography* swagger_ui_bundle/vendor/swagger-ui-2* connexion/vendor/swagger-ui*

# init-tf prepares the repo for Terraform commands. It assembles the partial S3 backend config as a JSON file, `aws_config.json`.
# This file is referenced by the TF_CLI_ARGS_init environment variable, which is set by running `source environment`.
init-tf:
	-rm -f $(TF_DATA_DIR)/*.tfstate
	mkdir -p $(TF_DATA_DIR)
	jq -n ".region=env.AWS_DEFAULT_REGION | .bucket=env.TF_S3_BUCKET | .key=env.APP_NAME+env.STAGE" > $(TF_DATA_DIR)/aws_config.json
	terraform init

destroy: init-tf
	terraform destroy

clean:
	git clean -Xdf dist .terraform* .chalice docs/_build tests/terraform/.terraform

lint: build-chalice-config
	flake8 *.py $(APP_NAME) tests
	mypy $(APP_NAME) --ignore-missing-imports
	source environment
	scripts/build_chalice_tf_config.py
	unset TF_CLI_ARGS_init; cd tests/terraform; terraform init; terraform validate

test: lint docs build-chalice-config unit-test migration-test

unit-test: load-test-data
	coverage run --timid --source $(APP_NAME) -m unittest discover --start-directory tests/unit --top-level-directory . --verbose

integration-test: update-fixtures
	python -m unittest discover --start-directory tests/integration --top-level-directory . --verbose
	scripts/invoke-lambda bundle_event_handler tests/fixtures/mock_sqs_bundle_create_event.json
	scripts/invoke-lambda bundle_event_handler tests/fixtures/mock_sqs_bundle_delete_event.json

migration-test:
	python -m unittest discover --start-directory tests/migration --top-level-directory . --verbose

fetch:
	scripts/fetch.py

# create the database and apply migrations
init-db:
	python -m $(APP_NAME).db init

# apply all migration files to the database
migrate-db:
	python -m $(APP_NAME).db migrate

drop-db:
	python -m $(APP_NAME).db drop

load: init-db
	python -m $(APP_NAME).db load

load-test-data: init-db update-fixtures
	python -m $(APP_NAME).db load-test

update-fixtures:
	export TEST_BUNDLE_UUID=$$(hca dss get-bundles-all --replica aws | jq -r .bundles[2].uuid) TEST_BUNDLE_VERSION=$$(hca dss get-bundles-all --replica aws | jq -r .bundles[2].version); \
	envsubst < tests/fixtures/mock_sqs_bundle_create_event.json.template > tests/fixtures/mock_sqs_bundle_create_event.json; \
	envsubst < tests/fixtures/mock_sqs_bundle_delete_event.json.template > tests/fixtures/mock_sqs_bundle_delete_event.json

# Update just the Lambda application code, but not the dependencies, routes, or other infra. Use xargs to parallelize the process.
update-lambda: $(TFSTATE_FILE)
	zip -r dist/deployment.zip app.py $(APP_NAME) $(APP_NAME)-api.yml
	$(eval LAMBDA_SHA = $(shell sha256sum dist/deployment.zip | cut -f 1 -d ' ' | base64 --wrap=0))
	aws s3 cp dist/deployment.zip s3://$(TF_S3_BUCKET)/$(LAMBDA_SHA).zip
	terraform output --json $(APP_NAME) | jq -r '.|values[]' | egrep "^$(APP_NAME)-.+handler" | \
	 xargs -n 1 -P 8 -I % aws lambda update-function-code --function-name % --s3-bucket $(TF_S3_BUCKET) --s3-key $(LAMBDA_SHA).zip

get-logs:
	aws logs describe-log-groups --log-group-name-prefix /aws/lambda/$(APP_NAME)-$(STAGE) | \
	 jq -r .logGroups[].logGroupName | \
	 xargs -n 1 aegea logs --start-time=-5m

refresh-all-requirements:
	@echo -n '' >| requirements.txt
	@echo -n '' >| requirements-dev.txt
	@if [ $$(uname -s) == "Darwin" ]; then sleep 1; fi  # this is required because Darwin HFS+ only has second-resolution for timestamps.
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

docs:
	$(MAKE) -C docs html

# create a migration file for changes made to db table definitions inheriting from the SQLAlchemyBase in dcpquery/db
create-migration:
	alembic revision --autogenerate

.PHONY: deploy init-secrets install-webhooks install-secrets build-chalice-config package init-tf init-db destroy
.PHONY: clean lint test fetch init-db load load-test-data update-lambda get-logs refresh-all-requirements docs
.PHONY: create-migration migration-test update-fixtures
