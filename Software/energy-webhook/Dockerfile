# Dockerfile for sbv1307/energy-webhook image
FROM arm32v7/php:7.4-apache

#FROM arm32v7/php:apache
LABEL "Name"="Apahe webhook Version=3.0.0"

# Update the package index files to get the latest list of available packages in the repositories.
# Upgrade: downloads and installs the updates for each outdated package and dependency on your system.
RUN apt-get update && apt-get upgrade -y

# Install PHP Redis client 
# Installation from sources by git clone https://github.com/phpredis/phpredis.git. Copy files to Docker image and install
WORKDIR /opt/phpredis
COPY ../phpredis .

# Install PHP Redis Client
RUN phpize
RUN ./configure
RUN make install

# Enable the PHP Redis client module in the PHP config file. 
WORKDIR /usr/local/etc/php/conf.d
RUN echo "extension=redis.so" > redis.ini

# Install PostgreSQL client
RUN apt-get update && apt-get upgrade -y
RUN apt-get install libpq-dev -y
RUN docker-php-ext-install pgsql

# Copy .bash_aliases and Invoked as an interactive non-login shell
WORKDIR /root
COPY ../bash_aliases .bash_aliases
RUN echo "[ -f ~/.bash_aliases ] && . ~/.bash_aliases" >> /root/.bashrc

# AH00558: apache2: Could not reliably determine the server's fully qualified domain name
RUN echo "ServerName localhost" >> /etc/apache2/apache2.conf

# Set workking directory for the webhook server. /var/www/html/ is the default DocumentRoot
WORKDIR /var/www/html/

# Copy only files from www/html
COPY ./www/html/* .
