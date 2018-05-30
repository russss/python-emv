test:
	pytest

upload:
	rm -Rf ./dist
	python ./setup.py bdist_wheel
	twine upload ./dist/*
