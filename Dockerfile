FROM harbor.imio.be/common/base:py3-ubuntu-22.04
ARG repo=imio.webservice.json
USER imio
RUN mkdir /home/imio/.buildout \
 && mkdir /home/imio/.buildout/downloads \
 && mkdir /home/imio/.buildout/eggs \
 && mkdir /home/imio/data \
 && mkdir /home/imio/config
ENV PIP=24.1.2 \
  HOME=/home/imio
COPY --chown=imio:imio default.cfg /home/imio/.buildout/default.cfg
USER root
RUN buildDeps="python3-pip build-essential libpq-dev libreadline-dev wget git gcc libc6-dev libpcre3-dev libssl-dev libxml2-dev libxslt1-dev libbz2-dev libffi-dev libjpeg62-dev libopenjp2-7-dev zlib1g-dev python3-dev" \
  && dependencies="postgresql-client-14 libpq-dev netcat" \
  && cd /home/imio/ \
  && apt-get update \
  && apt-get install -y --no-install-recommends $buildDeps \
  && apt-get install -y $dependencies \
  && pip install pip==$PIP
USER imio
WORKDIR /home/imio

COPY --chown=imio:imio . ${repo}
# RUN git clone https://github.com/IMIO/${repo}.git ${repo} \
RUN cd /home/imio/${repo} \
  && pip install -U setuptools \
  && pip install -r requirements.txt \
  && /home/imio/.local/bin/buildout -t 30 -c prod.cfg

USER root
RUN cd /home/imio/ \
  && rm -rf /home/imio/.buildout/downloads/ /var/lib/apt/lists/* /tmp/* /var/tmp/* /home/imio/.cache /home/imio/.local \
  && chown -R imio:imio /home/imio \
  && apt-get clean autoclean \
  && apt-get purge -y $buildDeps \
  && apt-get autoremove -y
VOLUME /home/imio/data
VOLUME /home/imio/config

COPY --chown=imio:imio start.sh /
EXPOSE 6543

CMD ["/start.sh"]
