FROM ubuntu:22.04@sha256:3d1556a8a18cf5307b121e0a98e93f1ddf1f3f8e092f1fddfd941254785b95d7

ENV user pwn
ENV chall_port 8080

RUN apt-get update
RUN apt-get -y install socat

RUN adduser -u 1337 $user

ADD ./flag /home/$user/flag
ADD ./deploy/prob /home/$user/prob

RUN chown root:$user /home/$user/flag
RUN chown root:$user /home/$user/prob

RUN chmod +x /home/$user/prob
RUN chmod 440 /home/$user/flag

WORKDIR /home/$user
USER $user
EXPOSE $chall_port

CMD socat TCP-L:8080,reuseaddr,fork, EXEC:"./prob"
