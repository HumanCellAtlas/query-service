.PHONY: install build stage deploy clobber
include ../common.mk

LAMBDA_NAME=load_data
ZIP_FILE=$(LAMBDA_NAME).zip
BUCKET=query-service-lambda-deployment-$(AWS_ACCOUNT_ID)
STAGED_FILE_KEY=$(DEPLOYMENT_STAGE)/$(LAMBDA_NAME)/$(ZIP_FILE)

default: build

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

	cp -R ../query/__init__.py target/query
	cp -R ../query/lambdas target/query
	cp -R ../query/lib target/query
	cp -R ../query/scripts target/query

	cp -R *.py target/
	# build.zip contains the psycopg2-3.6 package downloaded from https://github.com/jkehler/awslambda-psycopg2
	# and renamed psycopg2
	unzip build.zip
	cp -R build/ target/
	rm -rf build
	shopt -s nullglob; for wheel in vendor.in/*/*.whl; do unzip -q -o -d vendor $$wheel; done

	cp -R vendor/* target/

	cd target && zip -r ../$(ZIP_FILE) *

stage: build
	aws s3 cp $(ZIP_FILE) s3://$(BUCKET)/$(STAGED_FILE_KEY)

deploy: stage
	aws lambda update-function-code --function-name query-load-data-$(DEPLOYMENT_STAGE) --s3-bucket $(BUCKET) --s3-key $(STAGED_FILE_KEY)

clobber: ;
