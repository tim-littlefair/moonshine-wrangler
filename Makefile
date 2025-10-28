# Makefile for the moonshine-wrangler project
# Author: Tim Littlefair, October 2025

# Note that  the development environment for this project
# is Ubuntu Linux 24.04.
# As for all Debian-based Linuxes, the 'pip' command 
# which runs under the 'init' make target will fail 
# unless a virtual environment has been activated
# in the project directory before the 'make' command

.PHONY: init clean test check .venv_reminder test

init: .venv3
	pip install -r requirements.txt || make .venv_reminder

.venv3:
	python -m venv .venv3
	make .venv_reminder

test:
	pytest tests
	make check

clean:
	rm -rf .venv3

check:
	flake8 moonshinewrangler
	pycodestyle moonshinewrangler

.venv_reminder:
	echo Please run 'source .venv3/bin/activate' before attempting to run 'make'
