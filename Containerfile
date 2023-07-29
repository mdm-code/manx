FROM python:3.10
COPY . /app
WORKDIR app
RUN python -m pip install -e .
EXPOSE 8000
ENTRYPOINT [ "manx" ]
CMD [ "api" ]
