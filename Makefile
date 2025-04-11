.PHONY: lint redis
lint:
	black repensedb/ tests/
	flake8 repensedb/ tests/

redis:
	/home/samuelbaptista/.fly/bin/flyctl redis connect

