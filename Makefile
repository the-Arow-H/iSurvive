.PHONY: margin test serve verify

margin:
	python -m isurvive margin

test:
	python -m isurvive margin
	pytest -q

serve:
	python -m isurvive serve

verify:
	python -m isurvive verify-host
