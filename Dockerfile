FROM python

RUN pip install -r requirements.txt
COPY . /presence
WORKDIR /presence

EXPOSE 8000
ENTRYPOINT ["gunicorn"]
CMD ["server:api", "--bind=0.0.0.0:8000"]
