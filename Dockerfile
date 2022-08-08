FROM docker.cpartdc01.sherwin.com/ubuntu:20.04
USER root
COPY app/ /app
ADD http://swroot.sherwin.com/swroot.pem /etc/pki/ca-trust/source/anchors/swroot.crt
RUN echo 'APT::Acquire::Retries "3";' > /etc/apt/apt.conf.d/80-retries  && \
    apt-get update  && \
    apt-get install -y ca-certificates  && \
    apt-get upgrade -y && \
    unset http_proxy && \
    useradd flask && \
    apt-get install -y python3 python3-pip openssl && \
    pip3 install --upgrade pip && \
    pip3 install -r /app/requirements.txt && \
    rm -rf /var/cache/dnf && \
    chown -R flask: /app
ENV PORT 7070
EXPOSE 7070
WORKDIR /app
HEALTHCHECK CMD curl -k --fail https://localhost:7070/health | grep 'ok' || exit 1
CMD cd /app; /app/rungunicorn.sh
