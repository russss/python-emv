test:
	pytest

upload:
	rm -Rf ./dist
	python3 ./setup.py bdist_wheel
	twine upload ./dist/*
