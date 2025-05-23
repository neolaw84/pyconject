ifeq ($(OS),Windows_NT)
SHELL := powershell.exe
.SHELLFLAGS := -NoProfile -Command
endif

$(info SHELL is "$(SHELL)")

install-dev-reqs:
	@pip install -r dev-requirements.txt

clean:
	@pip uninstall -y pyconject
	@python rm.py -r -f dist 

lint:
	@python -m black .

build:
	@python -m build 

install-reqs:
	@pip install -r requirements.txt

install:
	cp dist/*.tar.gz ./pyconject.tar.gz
	python -m pip install ./pyconject.tar.gz
	python rm.py -r -f ./pyconject.tar.gz

test:
	@pytest --cov src --cov-report term-missing --exitfirst --cov-fail-under=80 tests

install-and-test: clean build install
	@pytest --override-ini=pythonpath="tests" tests

show-bump:
	bump-my-version show-bump

bump-micro:
	bump-my-version bump --allow-dirty micro

bump-minor:
	bump-my-version bump --allow-dirty minor 

bump-major:
	bump-my-version bump --allow-dirty major