FROM manage-django:base
WORKDIR /opt/teligen-ui
COPY app/ .
COPY start.sh /start.sh
