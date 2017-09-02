# First target is the default. Trigger it by running "make"
#  Do not invoke directly, please invoke from top-level Makefile
#  which creates the needed venv
package: zip_all

ZIP_TOP=../../output/functions
THOR_ZIP=$(ZIP_TOP)/thor.zip

zip_all: zip_thor
	@echo "Done packaging"

zip_thor:
	@echo "Packaging thor source to zip..." && \
	cd thor && \
	zip -qr $(THOR_ZIP) * && \
	cd ../../venv/lib/python2.7/site-packages && \
	zip -qr ../../$(THOR_ZIP) *
