ARG PYTHON_VERSION=3.10
ARG ALPINE_VERSION=3.21

FROM python:${PYTHON_VERSION}-alpine${ALPINE_VERSION}

ARG HOST=0.0.0.0
ARG PORT=8000

ENV HOST=$HOST
ENV PORT=$PORT

WORKDIR "/opt/app"
COPY ./ ./

RUN \
    apk update && \
    apk add --no-cache --virtual .build-deps \
        linux-headers build-base autoconf g++ gcc libc-dev make && \
    python3 -m pip install --root-user-action ignore -U pip && \
    pip3 install --root-user-action ignore -r ./requirements.txt && \
    apk del .build-deps && \
    apk add npm && \
    ln -fs /usr/share/zoneinfo/Etc/UTC /etc/localtime

WORKDIR "/opt/app/frontend"
RUN \
    npm install && \
    npm run build
WORKDIR "/opt/app"

# https://docs.docker.com/reference/build-checks/json-args-recommended/
SHELL ["/bin/sh", "-c"]
CMD python3 -m uvicorn --host=$HOST --port=$PORT main:app --reload
