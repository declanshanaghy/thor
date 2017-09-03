
.PHONY: venv

AWS_DEFAULT_REGION=us-west-2

#####
#
# Colors
#
# Black        0;30     Dark Gray     1;30
# Red          0;31     Light Red     1;31
# Green        0;32     Light Green   1;32
# Brown/Orange 0;33     Yellow        1;33
# Blue         0;34     Light Blue    1;34
# Purple       0;35     Light Purple  1;35
# Cyan         0;36     Light Cyan    1;36
# Light Gray   0;37     White         1;37

NC=\033[0m        # No Color
RED=\033[0;31m
GRN=\033[0;32m
ORNG=\033[0;33m
PURPLE=\033[0;35m
YEL=\033[1;33m

OK=$(GRN)
WARN=$(PURPLE)
ERR=$(RED)

deploy:
	@echo "Deploying to $(AWS_DEFAULT_REGION)"
	@. venv/bin/activate && \
	    cd thor && \
	    AWS_DEFAULT_REGION=$(AWS_DEFAULT_REGION) chalice deploy

venv:
	@echo "Creating virtual environment" && \
	virtualenv --prompt "\n(venv: thor)" venv && \
	. venv/bin/activate && \
	    echo `which python` && pip install -U setuptools==18.5 && \
	    pip install -r thor/requirements.txt
