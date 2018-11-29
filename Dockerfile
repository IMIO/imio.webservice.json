FROM docker-staging.imio.be/base:latest

ARG repo=imio.webservice.json
RUN mkdir /home/imio/.buildout \
 && mkdir /home/imio/.buildout/downloads \
 && mkdir /home/imio/.buildout/eggs \
 && mkdir /home/imio/data \
 && mkdir /home/imio/config
ENV PIP=9.0.3 \
  HOME=/home/imio
COPY default.cfg /home/imio/.buildout/default.cfg
RUN buildDeps="python-pip build-essential libpq-dev libreadline-dev wget git gcc libc6-dev libpcre3-dev libssl-dev libxml2-dev libxslt1-dev libbz2-dev libffi-dev libjpeg62-dev libopenjp2-7-dev zlib1g-dev python-dev" \
  && dependencies="postgresql-client-9.5 libpq-dev netcat" \
  && cd /home/imio/ \
  && apt-get update \
  && apt-get install -y --no-install-recommends $buildDeps \
  && apt-get install -y $dependencies \
  && pip install pip==$PIP \
  && git clone https://github.com/IMIO/${repo}.git ${repo} \
  && cd /home/imio/${repo} \
  && pip install -U setuptools \
  && pip install -r requirements.txt \
  && buildout -t 30 -c prod.cfg \
  && cd /home/imio/ \
  && rm -rf /home/imio/.buildout/downloads/ /var/lib/apt/lists/* /tmp/* /var/tmp/* /home/imio/.cache /home/imio/.local \
  && chown -R imio:imio /home/imio \
  && apt-get clean autoclean \
  && apt-get purge -y $buildDeps \
  && apt-get autoremove -y
VOLUME /home/imio/data
VOLUME /home/imio/config

COPY start.sh /
EXPOSE 6543

CMD ["/start.sh"]
