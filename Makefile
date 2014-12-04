.PHONY: clean-pyc clean-build docs

help:
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "config - install config and scripts in virtualenv"
	@echo "coverage - run coverage test"
	@echo "lint - check style with pylint"
	@echo "test - run tests"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "sdist - package"

clean: clean-build clean-pyc

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

config:
	pip install -e .[develop]

lint:
	pylint --rcfile=.pylint.rc monit-master tests ftests


test:
	py.test -v --cov-report term --cov monit-master tests


coverage:
	py.test -v --cov-report html --cov monit-master tests
	open htmlcov/index.html

docs:
	rm -f docs/monit-master.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ monit-master
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	@echo "open docs/_build/html/index.html"

sdist: clean docs test ftest
	python setup.py sdist
	ls -l dist
