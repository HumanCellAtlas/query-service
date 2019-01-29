.PHONY: deploy
include ../common.mk

LAMBDA_NAME=create_async_query
ZIP_FILE=$(LAMBDA_NAME).zip
BUCKET=query-service-$(AWS_ACCOUNT_ID)
STAGED_FILE_KEY=$(DEPLOYMENT_STAGE)/lambda_deployments/$(LAMBDA_NAME)/$(ZIP_FILE)

deploy: stage
	aws lambda update-function-code --function-name query-create-async-query-$(DEPLOYMENT_STAGE) --s3-bucket $(BUCKET) --s3-key $(STAGED_FILE_KEY)
