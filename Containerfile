FROM python:3.10
COPY . /app
WORKDIR app
RUN python -m pip install -e .
RUN python -m pip install --upgrade pip
EXPOSE 8000
ENTRYPOINT [ "manx" ]
CMD [ "api" ]
