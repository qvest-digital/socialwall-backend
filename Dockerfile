FROM python:3.7.3-alpine3.9

ENV PYTHONPATH /backend
ENV APP $PYTHONPATH/tarentsocialwall
ENV TZ 'Europe/Berlin'

RUN echo $TZ > /etc/timezone


WORKDIR $APP

COPY tarentsocialwall .

RUN ls -la $APP/*
RUN echo "===> Installing dependencies"
RUN pip3 install --user python-dateutil
RUN pip3 install --user --upgrade google-api-python-client
RUN pip3 install --user schedule
RUN apk add build-base openldap-dev python3-dev python2-dev
RUN pip3 install --user --upgrade python-ldap
RUN pip3 install  --user -r requirements.txt
