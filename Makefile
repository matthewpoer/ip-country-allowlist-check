
TIMESTAMP := $(shell date +"%s")
docker-image:
	docker build \
		--tag ip-country-allowlist-check:$(TIMESTAMP) \
		--tag ip-country-allowlist-check:latest \
		.

docker-run:
	docker run -p 5000:5000 -it --rm ip-country-allowlist-check

lint:
	pylint handler.py

run:
	FLASK_APP=handler.py flask run
