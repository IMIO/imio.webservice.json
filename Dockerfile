FROM harbor.imio.be/common/base:py3-ubuntu-26.04 AS builder

# TODO INFRA-6907: Replace UV copy with UV from base image on Harbor
COPY --from=ghcr.io/astral-sh/uv:0.9.2 /uv /bin/uv
# The venv uses the system Python 3.14 of the base image
ENV UV_COMPILE_BYTECODE=1 \
  UV_LINK_MODE=copy \
  UV_PYTHON_PREFERENCE=only-system
# psycopg2 has no wheel: it is compiled against libpq and the Python headers
RUN apt-get update \
  && apt-get install -y --no-install-recommends build-essential libpq-dev python3.14-dev \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /home/imio/imio.webservice.json
# The prod group installs imio.amqp and imio.dataexchange.* from PyPI, as pinned in
# uv.lock. --frozen because --locked would also check the dev group, which needs devel/
COPY pyproject.toml uv.lock .python-version README.rst MANIFEST.in ./
RUN uv sync --frozen --no-default-groups --group prod --no-editable --no-install-project
COPY imiowebservicejson imiowebservicejson
RUN uv sync --frozen --no-default-groups --group prod --no-editable


FROM harbor.imio.be/common/base:py3-ubuntu-26.04

# netcat for start.sh, postgresql-client for bin/connect_db
RUN apt-get update \
  && apt-get install -y --no-install-recommends libpq5 netcat-openbsd postgresql-client \
  && rm -rf /var/lib/apt/lists/* \
  && mkdir /home/imio/data /home/imio/config \
  && chown imio:imio /home/imio/data /home/imio/config
COPY --from=builder --chown=imio:imio /home/imio/imio.webservice.json/.venv /home/imio/imio.webservice.json/.venv
ENV PATH=/home/imio/imio.webservice.json/.venv/bin:$PATH \
  HOME=/home/imio
USER imio
WORKDIR /home/imio/imio.webservice.json
VOLUME /home/imio/data
VOLUME /home/imio/config

COPY start.sh /
EXPOSE 6543

CMD ["/start.sh"]
