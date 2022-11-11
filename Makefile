# Shortcut commands

test:
	@coverage run -m unittest discover -s tests

html-report:
	@coverage html
	@python -m webbrowser htmlcov/index.html

build:
	@python setup.py sdist bdist_wheel

clean:
	@rm -r ach_file.egg-info
	@rm -r build
	@rm -r dist
