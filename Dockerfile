FROM python:3.6
MAINTAINER edX <oscm@edx.org>

ADD . /app

WORKDIR /app

RUN make requirements
RUN pip install -e .

VOLUME /app
EXPOSE 8000
ENTRYPOINT ["python"]
CMD ["manage.py", "runserver"]
