# Query Service
[![](https://status.dev.data.humancellatlas.org/build/HumanCellAtlas/query-service/master.svg)](https://allspark.dev.data.humancellatlas.org/HumanCellAtlas/query-service/pipelines)

Placeholder for the Metadata Query Service


## Getting Started
create virtualenv and install dependencies
```bash
mkdir venv
virtualenv --python python3.6 venv/36
source venv/36/bin/activate
pip install -r requirements.txt
```
## Terraform
set DEPLOYMENT_STAGE and AWS_PROFILE
```bash
source environment
cd terraform
make secrets
make init
make plan
make apply

```

## Components
https://www.lucidchart.com/invitations/accept/02e38662-6da1-48ad-87ac-0355bb3a03d8

## Deployment
set DEPLOYMENT_STAGE and AWS_PROFILE
```bash
source environment
make secrets -C terraform/
make init -C terraform/
make plan -C terraform/
make apply -C terraform/
make deploy -C query/
```
## Tests
```bash
make install tests -C query/
```
