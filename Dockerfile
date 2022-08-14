FROM python:3.11-rc-slim
LABEL maintainer Rog3rSm1th <r0g3r5@protonmail.com>
RUN pip3 install kharma
WORKDIR /app
ENTRYPOINT  ["kharma"]