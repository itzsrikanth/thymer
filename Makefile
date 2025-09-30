.PHONY: install run build clean venv install-venv

install:
	pip install -e ".[dev]"

# Create virtual environment and install
venv:
	python3 -m venv venv
	venv/bin/python3 -m pip install --upgrade pip
	@echo "Virtual environment created. Activate with: source venv/bin/activate"

install-venv: venv
	venv/bin/pip install -e ".[dev]"
	@echo "Installed in virtual environment. Activate with: source venv/bin/activate"

run:
	python3 -m src

# Run without installing (just install deps)
run-direct:
	pip install -r requirements.txt
	python3 -m src

build:
	python3 build.py

clean:
	rm -rf build/ dist/ *.egg-info/ thymer.build/ thymer.dist/ thymer.onefile-build/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
