ARG PYTHON_VERSION=3.12
ARG ALPINE_VERSION=3.21

FROM python:${PYTHON_VERSION}-alpine${ALPINE_VERSION}

ARG HOST=0.0.0.0
ARG PORT=8000

ENV HOST=$HOST
ENV PORT=$PORT

# ホストのファイルをコンテナにコピー(.gitも含む)
WORKDIR "/opt/app"
COPY ./ ./

# NOTE: poetry installは2回実行しないとpoetry_dynamic_versioningがバージョンを正しく割り当てない
# (1回目は 0.0.0 のままで、2回目で正しいバージョンが割り当てられる)
RUN \
    apk update && \
    apk add --no-cache --virtual .build-deps \
        git linux-headers build-base autoconf g++ gcc libc-dev make && \
    python3 -m pip install --root-user-action ignore -U pip setuptools poetry && \
    poetry config virtualenvs.create false && \
    poetry install --without dev && \
    poetry install --without dev && \
    rm -rf ./.git/ && \
    apk del .build-deps && \
    apk add npm && \
    ln -fs /usr/share/zoneinfo/Etc/UTC /etc/localtime

WORKDIR "/opt/app/frontend"
RUN \
    npm install && \
    npm run build && \
    rm -rf ./node_modules/
WORKDIR "/opt/app"

# https://docs.docker.com/reference/build-checks/json-args-recommended/
SHELL ["/bin/sh", "-c"]
CMD python3 -m uvicorn --host=$HOST --port=$PORT main:app --reload
