#use a dynamic build image, with a default value
ARG BASE_IMAGE=python:3.8-slim
FROM ${BASE_IMAGE} AS build
#FROM python38build AS build

#update and install dependencies
RUN apt-get update \
    && apt-get install -y \
    curl \
    apt-transport-https \
    gnupg2 \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && apt-get install -y \
    unixodbc
# download and install msodbcsql17 manually
RUN TEMP_DEB="$(mktemp)" \
    && curl -o "$TEMP_DEB" 'https://packages.microsoft.com/debian/10/prod/pool/main/m/msodbcsql17/msodbcsql17_17.7.1.1-1_amd64.deb' \
    && yes | dpkg --skip-same-version -i "$TEMP_DEB" \
    && rm -f "$TEMP_DEB"
# to be sure if it can download and install from official way
RUN curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    && apt-get install -y build-essential libcurl4-gnutls-dev libxml2-dev libssl-dev unixodbc-dev libgssapi-krb5-2
RUN apt update && apt install -y openjdk-11-jdk

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
WORKDIR /app
COPY ["requirements.txt", "dev-requirements.txt", "./"]

ENV PIP_DISABLE_PIP_VERSION_CHECK=1
RUN . /opt/venv/bin/activate && pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir -r dev-requirements.txt
COPY . .

# Python defaults to ASCII encoding. Switch to UTF-8
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

EXPOSE 80
CMD [ "/bin/sh", "./run-docker.sh" ]