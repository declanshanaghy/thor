
.PHONY: venv deploy webapp

CWD := $(shell pwd)

AWS_DEFAULT_REGION := us-west-2
STACK := thor-20180703
BUCKET := thor-20180703
DEPLOY_USER := ec2-user
DEPLOY_TGT := 54.218.150.106

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

delpoy: cfn webapp

cfn:
	@echo "Updating CloudFormation stack: $(STACK)..."
	@aws s3 cp templates/thor.yml s3://$(BUCKET)/thor.yml
	@aws --region $(AWS_DEFAULT_REGION) cloudformation update-stack \
	    --stack-name $(STACK) \
	    --template-url http://$(BUCKET).s3-$(AWS_DEFAULT_REGION).amazonaws.com/thor.yml || true

webapp:
	@echo "Deploying to $(DEPLOY_TGT)"
	@rsync -avzl --exclude=*.pyc -e ssh webapp ${DEPLOY_USER}@${DEPLOY_TGT}:~/thor/
	@ssh ${DEPLOY_USER}@${DEPLOY_TGT} bash -s < update_webapp.sh

venv:
	@echo "Creating virtual environment" && \
	virtualenv --prompt "\n(venv: thor)" venv && \
	. venv/bin/activate && \
	    echo `which python` && \
	    pip install -U setuptools && \
	    pip install -U pip \
	    pip install -r requirements.txt
