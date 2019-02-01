export AWS_ACCOUNT_ID=$(shell aws sts get-caller-identity | jq -r .Account)
export LOAD_DATA_QUEUE_URL=NO_LD_QUEUE_URL
export ASYNC_QUERY_QUEUE_URL=NO_LQ_QUEUE_URL

.PHONY: install
install:
	virtualenv -p python3 venv
	venv/bin/pip install -r requirements-dev.txt --upgrade

.PHONY: unit-test
unit-test:
	. venv/bin/activate \
	&& coverage run -m unittest discover -s test/unit -p 'test_*.py' --top-level-directory . --verbose

.PHONY: functional-tests
functional-tests:
	python -m unittest discover --start-directory test/functional --top-level-directory . --verbose

.PHONY: tests
tests: unit-test functional-tests

.PHONY: report
report:
	coverage report --omit=venv/*

.PHONY: deploy
deploy:
	$(MAKE) -C ../chalice $@
	$(MAKE) -C ../load_data_lambda $@
	$(MAKE) -C ../async_query_lambda $@

.PHONY: lint
lint:
	. venv/bin/activate && flake8
