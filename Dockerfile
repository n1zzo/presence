FROM python

COPY . /presence
WORKDIR /presence
RUN pip install -r requirements.txt

EXPOSE 8000
ENTRYPOINT ["gunicorn"]
CMD ["server:api", "--bind=0.0.0.0:8000"]
