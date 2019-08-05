
.PHONY: venv deploy webapp

CWD := $(shell pwd)

AWS_DEFAULT_REGION := us-west-2
BUCKET := thor-20180703
STACK := thor-20180703-gen02
DEPLOY_USER := ec2-user
DEPLOY_TGT := 52.32.115.39
TEMPLATE_URL := http://$(BUCKET).s3-$(AWS_DEFAULT_REGION).amazonaws.com/thor.yml

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

template:
	@echo "Updating CloudFormation stack: $(STACK)"
	@aws s3 cp templates/thor.yml s3://$(BUCKET)/thor.yml
	@echo "Template is available at: $(TEMPLATE_URL)"

cfn:
	@aws --region $(AWS_DEFAULT_REGION) cloudformation update-stack \
	    --stack-name $(STACK) \
	    --template-url $(TEMPLATE_URL) || true

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
	    pip install -U pip awscli && \
	    pip install -r webapp/requirements.txt
