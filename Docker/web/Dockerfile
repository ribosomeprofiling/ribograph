FROM python:3.7

###############################################################
####  Install Required Packages  ##############################
###############################################################
RUN apt-get update --fix-missing && \
  apt-get install -q -y wget curl bzip2 libbz2-dev git build-essential zlib1g-dev locales vim fontconfig locales gfortran libopenblas-dev liblapack-dev

# Install nodejs
RUN curl -sL https://deb.nodesource.com/setup_16.x | bash - \
  && apt-get update --fix-missing \
  && apt-get install -y nodejs \
  && curl -L https://www.npmjs.com/install.sh | sh

# Set the locale
RUN locale-gen en_US.UTF-8  
ENV LANGUAGE en_US:en  

ADD requirements.txt ./

RUN pip install -r requirements.txt



###############################################################
#### Arrange ENV and entrypoint ###############################
###############################################################

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV HOME=/home/ribograph
ENV APP_HOME=/home/ribograph/web

RUN mkdir -p $APP_HOME

WORKDIR $APP_HOME


# This file should have been mounted
ENTRYPOINT ["bash","/usr/src/app/entrypoint.sh"]
