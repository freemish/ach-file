# Shortcut commands

test:
	@coverage run -m unittest discover -s tests

html-report:
	@coverage html
	@python -m webbrowser htmlcov/index.html
