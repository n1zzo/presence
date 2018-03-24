FROM python

COPY requirements.txt /presence/requirements.txt
RUN pip install -r /presence/requirements.txt
COPY . /presence
WORKDIR /presence

EXPOSE 8000
ENTRYPOINT ["gunicorn"]
CMD ["server:api", "--bind=0.0.0.0:8000"]
