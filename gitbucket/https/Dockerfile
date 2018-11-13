FROM skywind3000/gitbucket:default
MAINTAINER skywind3000 "https://github.com/skywind3000"

COPY build /tmp/build

RUN chmod -R 755 /tmp/build/script/*
RUN run-parts --exit-on-error /tmp/build/script && rm -rf /tmp/build

EXPOSE 8443
EXPOSE 8080

CMD [ "/usr/local/tomcat/bin/catalina.sh", "run"  ]


