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
	cp ../requirements.txt .
	mkdir -p chalicelib/query/lib
	mkdir -p chalicelib/query/lambdas
	mkdir -p chalicelib/config
	cp -R ../query/lib/common chalicelib/query/lib/common
	cp -R ../query/lib/__init__.py chalicelib/query/lib
	cp -R ../query/lambdas/__init__.py \
		  ../query/lambdas/api_server \
		chalicelib/query/lambdas
	envsubst '$$API_HOST' < ../config/query-api.yml > chalicelib/config/query-api.yml
	shopt -s nullglob; for wheel in vendor.in/*/*.whl; do unzip -q -o -d vendor $$wheel; done

deploy: build
	@echo -e "\n\n#########################################################"
	@echo -e "########## Deploying to $(DEPLOYMENT_STAGE) environment"
	@echo -e "#########################################################\n"
	./build_deploy_config.sh $(DEPLOYMENT_STAGE)
	chalice deploy --no-autogen-policy --stage $(DEPLOYMENT_STAGE) --api-gateway-stage $(DEPLOYMENT_STAGE)