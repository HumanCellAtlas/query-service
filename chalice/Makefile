include ../common.mk

export EXPORT_ENV_VARS_TO_LAMBDA=DEPLOYMENT_STAGE \
			API_HOST

clean:
	git clean -df .

clobber: clean
	git checkout .chalice/*.json

build:
	rm -rf chalicelib/config
	rm -rf chalicelib/query

	mkdir -p chalicelib/query/lib
	mkdir -p chalicelib/query/lambdas
	mkdir -p chalicelib/config

	cp index.html chalicelib/


	cp -R ../query/__init__.py chalicelib/query
	cp -R ../query/lib chalicelib/query
	cp -R ../query/lambdas/__init__.py \
		  ../query/lambdas/api_server \
		chalicelib/query/lambdas
	envsubst '$$API_HOST' < ../config/query-api.yml > chalicelib/config/query-api.yml
	shopt -s nullglob; for wheel in vendor.in/*/*.whl; do unzip -q -o -d vendor $$wheel; done

	# build.zip contains the psycopg2-3.6 package downloaded from https://github.com/jkehler/awslambda-psycopg2
	# and renamed psycopg2
	unzip build.zip
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
