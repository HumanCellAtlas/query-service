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
pip install -r requirements-dev.txt
```
## Terraform
```bash
source environment
export AWS_PROFILE=hca
cd terraform
make secret
make init
make plan
make apply

```

## Components
## Deployment
## Tests
