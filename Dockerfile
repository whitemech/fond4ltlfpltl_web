FROM ubuntu:18.04

USER root

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y dialog && \
    apt-get install -y apt-utils && \
    apt-get upgrade -y && \
    apt-get install -y sudo

# other dependencies
RUN apt-get install -y build-essential && \
    apt-get install -y python3.7     && \
    apt-get install -y python3-pip && \
    apt-get install -y openjdk-8-jre-headless && \
    apt-get install -y wget && \
    apt-get install -y git && \
    apt-get install -y time && \
    apt-get install -y gawk && \
    apt-get install -y libtool && \
    apt-get install -y graphviz && \
    apt-get install -y curl

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 1 \
    && update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1
RUN pip3 install --upgrade pip

#RUN ln -s /usr/bin/local/pip3 /usr/bin/pip

# Flex & Bison & Graphviz
RUN apt-get install -y flex && \
    apt-get install -y bison && \
    apt-get install -y libgraphviz-dev

# MONA
#RUN wget https://github.com/whitemech/MONA/archive/refs/tags/v1.4-19.dev0.tar.gz &&\
#    tar -xf v1.4-19.dev0.tar.gz &&\
#    cd MONA-1.4-19.dev0 &&\
#    ./configure &&\
#    make &&\
#    make install

RUN apt-get install mona

EXPOSE 5000
WORKDIR /fond4ltlfpltl_web

COPY . .

RUN pip3 install -r requirements.txt
RUN pip3 install gunicorn

CMD gunicorn --bind 0.0.0.0:$PORT fond4ltlfpltl_web:app

#CMD ["python", "fond4ltlfpltl_web.py"]
