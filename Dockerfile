FROM python:2.7.18

EXPOSE 8467

ENV PRUNE_EMPTY=True
ENV LOG_LEVEL=info
ENV LOG_STDOUT=True
ENV LOG_DATA_STDOUT=True
ENV LOG_FS_ENABLED=False
#ENV LOG_REQUESTS=raw:metrics:events
#ENV S3_BUCKET=thor-20180703
#ENV LOG_DIR=/tmp/logs
#ENV CREDS_DIR=/tmp/creds

COPY webapp /webapp
RUN pip install -r webapp/requirements.txt

CMD ["python2", "/webapp/asciiwh.py"]