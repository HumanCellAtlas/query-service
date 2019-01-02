.PHONY: install
install:
	virtualenv -p python3 venv
	venv/bin/pip install -r requirements-dev.txt --upgrade

.PHONY: test
test:
	. venv/bin/activate \
	&& coverage run -m unittest discover -s test/unit -p 'test_*.py' --top-level-directory . --verbose

.PHONY: functional-tests
functional-tests:
	python -m unittest discover --start-directory test/functional --top-level-directory . --verbose

.PHONY: report
report:
	coverage report --omit=venv/*

.PHONY: deploy
deploy:
	$(MAKE) -C ../chalice $@
	$(MAKE) -C ../load_data_lambda $@

