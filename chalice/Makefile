include ../common.mk
export LOAD_DATA_QUEUE_URL := 'ANYTHING'
export ASYNC_QUERY_QUEUE_URL := ANYTHING

export EXPORT_ENV_VARS_TO_LAMBDA=DEPLOYMENT_STAGE \
			API_HOST \
			LOAD_DATA_QUEUE_URL \
			ASYNC_QUERY_QUEUE_URL \
			AWS_ACCOUNT_ID

check-queue:
ifeq ($(DEPLOYMENT_STAGE),$(findstring $(DEPLOYMENT_STAGE),$(LOAD_DATA_QUEUE_URL)))
	@echo -e "CORRECT ENV FOR LOAD DATA QUEUE URL"
else
	$(error incorrect ENV: $(DEPLOYMENT_STAGE) FOR LOAD DATA QUEUE URL: $(LOAD_DATA_QUEUE_URL))
endif
ifeq ($(DEPLOYMENT_STAGE),$(findstring $(DEPLOYMENT_STAGE),$(ASYNC_QUERY_QUEUE_URL)))
	@echo -e "CORRECT ENV FOR ASYNC QUERY QUEUE URL"
else
	$(error incorrect ENV: $(DEPLOYMENT_STAGE) FOR LONG QUERY QUEUE URL: $(ASYNC_QUERY_QUEUE_URL))
endif

clean:
	git clean -df .

clobber: clean
	git checkout .chalice/*.json

build:
	rm -rf chalicelib/config
	rm -rf chalicelib/query

	mkdir -p chalicelib/config

	cp index.html chalicelib/

	rsync -av ../query chalicelib/ --exclude venv/ --exclude test/

	envsubst '$$API_HOST' < ../config/query-api.yml > chalicelib/config/query-api.yml
	shopt -s nullglob; for wheel in vendor.in/*/*.whl; do unzip -q -o -d vendor $$wheel; done

	# psycopg2.zip contains the psycopg2-3.6 package downloaded from https://github.com/jkehler/awslambda-psycopg2
	# and renamed psycopg2
	unzip psycopg2.zip
	rm -rf vendor/psycopg2
	cp -R build/psycopg2 vendor
	rm -rf build

deploy: build
	@echo -e "\n\n#########################################################"
	@echo -e "########## Deploying to $(DEPLOYMENT_STAGE) environment"
	@echo -e "#########################################################\n"
	./build_deploy_config.sh $(DEPLOYMENT_STAGE)
	chalice deploy --no-autogen-policy --stage $(DEPLOYMENT_STAGE) --api-gateway-stage $(DEPLOYMENT_STAGE)

.PHONY: build
