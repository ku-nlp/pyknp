.PHONY: deploy
deploy: build
	poetry publish

.PHONY: test-deploy
test-deploy: build
	poetry publish -r testpypi

.PHONY: build
build:
	poetry build

.PHONY: build-doc
build-doc:
	cd docs && make html

.PHONY: test
	python -m unittest discover -s pyknp -p '*.py'
