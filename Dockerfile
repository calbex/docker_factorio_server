FROM frolvlad/alpine-glibc:alpine-3.3_glibc-2.23

MAINTAINER calbex

WORKDIR /opt

COPY ./simple_launch.sh /opt/
COPY ./factorio.crt /opt/

VOLUME /opt/factorio/saves /opt/factorio/mods

EXPOSE 34197/udp
EXPOSE 27015/tcp

CMD ["./simple_launch.sh"]

ENV FACTORIO_AUTOSAVE_INTERVAL=2 \
    FACTORIO_AUTOSAVE_SLOTS=3 \
    FACTORIO_ALLOW_COMMANDS=false \
    FACTORIO_NO_AUTO_PAUSE=false \
    VERSION=0.15.9 \
    FACTORIO_SHA1=37c6623bad01b467bb000c17873d738e09197403 \
    FACTORIO_WAITING=false \
    FACTORIO_MODE=normal \
    FACTORIO_SERVER_NAME= \
    FACTORIO_SERVER_DESCRIPTION= \
    FACTORIO_SERVER_MAX_PLAYERS= \
    FACTORIO_SERVER_VISIBILITY= \
    FACTORIO_USER_USERNAME= \
    FACTORIO_USER_PASSWORD= \
#    FACTORIO_USER_TOKEN= \
    FACTORIO_SERVER_GAME_PASSWORD= \
    FACTORIO_SERVER_VERIFY_IDENTITY=

RUN apk --update add bash curl && \
    curl -sSL --cacert /opt/factorio.crt https://www.factorio.com/get-download/$VERSION/headless/linux64 -o /tmp/factorio_headless_x64_$VERSION.tar.xz && \
    echo "$FACTORIO_SHA1  /tmp/factorio_headless_x64_$VERSION.tar.xz" | sha1sum -c && \
    tar xJf /tmp/factorio_headless_x64_$VERSION.tar.xz && \
    rm /tmp/factorio_headless_x64_$VERSION.tar.xz
