.PHONY: install
install:
	virtualenv -p python3 venv
	venv/bin/pip install -r requirements-dev.txt --upgrade

.PHONY: test
test:
	. venv/bin/activate && python -m unittest discover -s test/unit -p 'test_*.py' --top-level-directory . --verbose

.PHONY: functional-tests
functional-tests:
	PYTHONWARNINGS=ignore:ResourceWarning python \
		-m unittest discover --start-directory test/functional --top-level-directory . --verbose


.PHONY: deploy
deploy:
	cd ../chalice && make deploy
	cd ../load_data_lambda && make deploy
