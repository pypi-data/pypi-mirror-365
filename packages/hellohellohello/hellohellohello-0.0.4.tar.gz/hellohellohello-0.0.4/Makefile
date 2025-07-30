build:
	hatch build

# These settings are used for publish creds
pypirc:
	cat ~/.pypirc

# TODO: Figure out how to this with Hatch
upload:
	twine upload -r pypi dist/*

# BUG: Error uploading to repository: pypi - Request URL is missing an 'http://' or 'https://' protocol.
publish:
	hatch publish --repo pypi 
