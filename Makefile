init:
	pip install pipenv
	pipenv install

test: init
	pipenv run pytest tests/.
