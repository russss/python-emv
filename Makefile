test:
	tox

upload:
	rm -Rf ./dist
	pandoc -f markdown -t rst ./README.md > ./README.rst
	python ./setup.py bdist_wheel
	twine upload ./dist/*
