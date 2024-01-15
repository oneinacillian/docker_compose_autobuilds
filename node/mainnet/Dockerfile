FROM ubuntu:20.04
RUN apt-get update && apt-get upgrade
WORKDIR /apps/wax
COPY ./files .
#COPY ./snapshot ./snapshots
RUN apt-get install ./wax-323wax01-hotfix_3.2.3wax01-hotfix-ubuntu-18.04_amd64.deb -y \
&& chmod +x start.sh \
&& chmod +x stop.sh

