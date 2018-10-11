
ENVS=dev integration prod staging
MODULES=database query-service-infra
ACCOUNTS=hca-id hca-prod humancellatlas

figlet_docker = docker run --rm mbentley/figlet

all: check

lint: lint-terraform

lint-terraform: lint-accounts lint-envs lint-modules

lint-accounts:
	@for account in $(ACCOUNTS); do \
		$(MAKE) -C terraform/accounts/$$account lint || exit $$?; \
	done

lint-envs:
	@for env in $(ENVS); do \
		$(MAKE) -C terraform/envs/$$env lint || exit $$?; \
	done; \
	$(figlet_docker) "global"; \
	$(MAKE) -C terraform/global lint || exit $$?

lint-modules:
	@for module in $(MODULES); do \
		$(MAKE) -C terraform/modules/$$module lint || exit $$?; \
	done

fmt: fmt-accounts fmt-envs fmt-global fmt-modules

fmt-accounts:
	@for account in $(ACCOUNTS); do \
		$(MAKE) -C terraform/accounts/$$account fmt || exit $$?; \
	done

fmt-envs:
	@for env in $(ENVS); do \
		$(MAKE) -C terraform/envs/$$env fmt || exit $$?; \
	done

fmt-global:
	$(MAKE) -C terraform/global fmt || exit $$?

fmt-modules:
	@for module in $(MODULES); do \
		$(MAKE) -C terraform/modules/$$module fmt || exit $$?; \
	done

docs: docs-envs docs-global docs-modules

docs-accounts:
	@for account in $(ACCOUNTS); do \
		$(MAKE) -C terraform/accounts/$$account docs || exit $$?; \
	done

docs-envs:
	@for env in $(ENVS); do \
		$(MAKE) -C terraform/envs/$$env docs || exit $$?; \
	done

docs-global:
	$(MAKE) -C terraform/global docs || exit $$?;

docs-modules:
	@for module in $(MODULES); do \
		$(MAKE) -C terraform/modules/$$module docs || exit $$?; \
	done

clean:

test:

check: check-plan check-docs

check-plan: check-plan-accounts check-plan-envs check-plan-global

check-plan-accounts:
	@for account in $(ACCOUNTS); do \
		$(figlet_docker) "accounts/$$account"; \
		$(MAKE) -C terraform/accounts/$$account check-plan || exit $$?; \
	done

check-plan-envs:
	@for env in $(ENVS); do \
		$(figlet_docker) "envs/$$env"; \
		$(MAKE) -C terraform/envs/$$env check-plan || exit $$?; \
	done

check-plan-global:
	$(figlet_docker) "global"; \
	$(MAKE) -C terraform/global check-plan || exit $$?

check-docs:
	@for mod in $(MODULES); do \
		$(MAKE) -C terraform/modules/$$module check-docs || exit $$?; \
	done

clean: clean-accounts clean-envs clean-global

clean-accounts:
	@for account in $(ACCOUNTS); do \
		$(figlet_docker) "accounts/$$account"; \
		$(MAKE) -C terraform/accounts/$$account clean || exit $$?; \
	done

clean-envs:
	@for env in $(ENVS); do \
		$(figlet_docker) "envs/$$env"; \
		$(MAKE) -C terraform/envs/$$env clean || exit $$?; \
	done

clean-global:
	$(figlet_docker) "global"; \
	$(MAKE) -C terraform/global clean || exit $$?

.PHONY: all check check-docs check-plan check-plan-accounts clean docs docs-accounts docs-envs docs-modules fmt fmt-accounts fmt-envs fmt-modules lint lint-accounts lint-envs lint-modules lint-terraform setup test

-include *.mk
