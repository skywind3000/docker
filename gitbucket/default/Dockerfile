FROM tomcat:9-alpine
MAINTAINER skywind3000
LABEL version=4.29.0
ENV DEBIAN_FRONTEND=noninteractive TERM=xterm GITBUCKET_HOME=/var/gitbucket
RUN rm -rf /usr/local/tomcat/webapps/ROOT
COPY gitbucket.war /usr/local/tomcat/webapps/ROOT.war
RUN (cd /usr/local/tomcat/webapps; ln -s ROOT.war gitbucket-4.29.0)
VOLUME $GITBUCKET_HOME
WORKDIR $GITBUCKET_HOME
EXPOSE 8080
EXPOSE 29418
CMD [ "/usr/local/tomcat/bin/catalina.sh", "run"  ]
