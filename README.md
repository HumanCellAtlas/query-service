# Query Service
[![](https://status.dev.data.humancellatlas.org/build/HumanCellAtlas/query-service/master.svg)](https://allspark.dev.data.humancellatlas.org/HumanCellAtlas/query-service/pipelines)

Placeholder for the Metadata Query Service


## Getting Started
create virtualenv and install dependencies
```bash
cd query-service
mkdir venv
virtualenv --python python3.6 venv/36
source venv/36/bin/activate
pip install -r requirements.txt
```
## Terraform
```bash
set DEPLOYMENT_STAGE
export AWS_PROFILE=hca
source environment
cd terraform
make secret
make init
make plan
make apply

```

## Components
## Deployment
```
set DEPLOYMENT_STAGE
export AWS_PROFILE=hca
source environment
cd terraform
make secret
make init
make plan
make apply
cd ../query
make deploy
```
## Tests
```
cd query/
make install test functional-tests
```
