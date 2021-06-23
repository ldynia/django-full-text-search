FROM python:3.7.9-alpine

ARG PORT=8000
ENV PORT=$PORT

ENV PYTHONUNBUFFERED=True
ENV PYTHONIOENCODING=UTF-8

WORKDIR /app
COPY . /app

RUN apk add \
    curl \
    gcc \
    libpq \
    musl-dev \
    postgresql-dev

# Fixed permissions, create exec:exec and dev:dev
RUN sed -i '/999/d;' /etc/group && \
    addgroup -S -g 999 exec && \
    adduser -u 999 -SDHG exec exec && \
    adduser -DH dev && \ 
    adduser exec dev

RUN chown -R exec:dev \
    /app \
    /usr/local/bin/ \
    /usr/local/lib/python3.7/

RUN chmod -R a-w /etc

EXPOSE ${PORT}
VOLUME /app

HEALTHCHECK CMD curl -f http://localhost:${PORT}/ || exit 1

USER exec:dev

ENTRYPOINT ["/app/scripts/startup.sh"]