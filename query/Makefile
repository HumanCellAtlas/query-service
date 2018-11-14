.PHONY: install
install:
	virtualenv -p python3 venv
	venv/bin/pip install -r requirements-dev.txt --upgrade

.PHONY: test
test:
	. venv/bin/activate && python3 -m unittest discover -s test -p 'test_*.py'

.PHONY: deploy
deploy:
	@echo "Nothing to deploy yet!"
