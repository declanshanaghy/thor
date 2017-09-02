# First target is the default. Trigger it by running "make"

REGION := us-west-2
BUCKET := thor-20170830
STACK := thor-20170830-2
BUILD_TIMESTAMP := $(shell date +'%Y%m%dT%H%M%S')

all: package s3put cfn_update

package: venv clean
	@echo Packaging...
	@mkdir -p output/functions; \
        . venv/bin/activate && \
        cd src && make

cfn_update:
	@echo "Updating stack..."
	aws --region $(REGION) cloudformation update-stack \
	    --capabilities CAPABILITY_IAM \
	    --stack-name $(STACK) \
	    --template-url https://s3.amazonaws.com/$(BUCKET)/thor.yml \
	    --parameters ParameterKey=BuildTimestamp,ParameterValue=$(BUILD_TIMESTAMP)

s3put:
	@s3put --region $(REGION) -b $(BUCKET) \
	    -p $(shell pwd)/output/functions \
	    -k $(BUILD_TIMESTAMP) \
	    output/functions/thor.zip
	@s3put --region $(REGION) -b $(BUCKET) \
	    -p $(shell pwd)/deploy \
	    deploy/thor.yml

venv:
	@echo "Creating virtual environment" && \
        virtualenv --prompt "\n(virtualenv: $(thor))" venv && \
        . venv/bin/activate && \
        echo `which python` && \
        pip install -U setuptools==18.5

clean:
	@echo Cleaning...
	@rm -rf output
	@rm -rf .coverage coverage.xml htmlcov
	@rm -rf dist .cache
	@rm -rf tests/clonedigger.xml tests/flake8.log tests/pylint.log tests/test-result.xml
	@find . -name "*.pyc" -delete
	@find . -name "*.pyo" -delete
	@find . -name "*,cover" -delete
	@find . -name .DS_Store -delete
	@find . -name __pycache__ -delete
