FROM ubuntu:18.04

USER root

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y sudo

# other dependencies
RUN apt-get install -y build-essential && \
    apt-get install -y python3 && \
    apt-get install -y python3-pip && \
    apt-get install -y openjdk-8-jre-headless && \
    apt-get install -y wget && \
    apt-get install -y git && \
    apt-get install -y time && \
    apt-get install -y gawk && \
    apt-get install -y libtool && \
    apt-get install -y graphviz && \
    apt-get install -y curl

RUN ln -s /usr/bin/python3 /usr/bin/python

ENV PYTHON_PIP_VERSION 21.1.2
# https://github.com/pypa/get-pip
ENV PYTHON_GET_PIP_URL https://github.com/pypa/get-pip/raw/936e08ce004d0b2fae8952c50f7ccce1bc578ce5/public/get-pip.py
ENV PYTHON_GET_PIP_SHA256 8890955d56a8262348470a76dc432825f61a84a54e2985a86cd520f656a6e220


RUN set -ex; \
	\
	wget -O get-pip.py "$PYTHON_GET_PIP_URL"; \
	echo "$PYTHON_GET_PIP_SHA256 *get-pip.py" | sha256sum -c -; \
	\
	python get-pip.py \
		--disable-pip-version-check \
		--no-cache-dir \
		"pip==$PYTHON_PIP_VERSION" \
	; \
	pip --version; \
	\
	find /usr/local -depth \
		\( \
			\( -type d -a \( -name test -o -name tests -o -name idle_test \) \) \
			-o \
			\( -type f -a \( -name '*.pyc' -o -name '*.pyo' \) \) \
		\) -exec rm -rf '{}' +; \
	rm -f get-pip.py

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

RUN pip install -r requirements.txt

RUN pip install gunicorn
CMD gunicorn --bind 0.0.0.0:$PORT fond4ltlfpltl_web:app

#CMD ["python", "fond4ltlfpltl_web.py"]
