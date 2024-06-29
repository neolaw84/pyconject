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
	python rm.py ./pyconject.tar.gz

test:
	@pytest tests 

install-and-test: clean build install
	@pytest --override-ini=pythonpath="src" tests