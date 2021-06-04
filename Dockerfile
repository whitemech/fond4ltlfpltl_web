FROM ubuntu:20.04

USER root

ENV DEBIAN_FRONTEND=noninteractive
ENV LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

RUN apt update && \
    apt upgrade -y && \
    apt install -y sudo

# other dependencies
RUN apt install -y build-essential && \
    apt install -y python3 && \
    apt install -y python3-pip && \
    apt install -y openjdk-8-jre-headless && \
    apt install -y wget && \
    apt install -y git && \
    apt install -y cmake && \
    apt install -y automake && \
    apt install -y libtool && \
    apt install -y graphviz

# Flex & Bison & Graphviz
RUN apt install -y flex && \
    apt install -y bison && \
    apt install -y libgraphviz-dev

# MONA
RUN apt install mona

# helper tools
RUN apt install -y curl

RUN ln -s /usr/bin/python3 /usr/bin/python

# install yarn
#RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add -
#RUN echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
#RUN apt update && apt install -y yarn

RUN pip install gunicorn

WORKDIR /fond4ltlfpltl
COPY . .

RUN pip install -r requirements.txt

#ARG REACT_APP_API_ENDPOINT=/
#ARG REACT_APP_API_HOSTNAME=localhost

#RUN cd /client && yarn install
#RUN cd /client && yarn build

#WORKDIR /fond4ltlfpltl_web

#CMD FLASK_STATIC_FOLDER=/fond4ltlfpltl_web gunicorn --bind 0.0.0.0:$PORT wsgi
CMD ["python", "fond4ltlfpltl_web.py"]