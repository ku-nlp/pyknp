.PHONY: deploy
deploy: build
	twine upload --skip-existing dist/*

.PHONY: test-deploy
test-deploy: build
	twine upload --skip-existing -r pypitest dist/*

.PHONY: build
build:
	python setup.py sdist --formats=zip

.PHONY: build-doc
build-doc:
	cd docs && make html
