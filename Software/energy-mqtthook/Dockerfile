# Dockerfile for sbv1307/energy-mqtthook image
FROM arm32v7/php:7.4-apache

#FROM arm32v7/php:apache
LABEL "Name"="Apahe mqtthook Version=1.0.0"

# Update the package index files to get the latest list of available packages in the repositories.
# Upgrade: downloads and installs the updates for each outdated package and dependency on your system.
RUN apt-get update && apt-get upgrade -y

# Install PHP Redis client 
# Installation from sources by git clone https://github.com/phpredis/phpredis.git. Copy files to Docker image and install
WORKDIR /opt/phpredis
COPY ./phpredis .

# Install PHP Redis Client
RUN phpize
RUN ./configure
RUN make install

# Enable the PHP Redis client module in the PHP config file. 
WORKDIR /usr/local/etc/php/conf.d
RUN echo "extension=redis.so" > redis.ini

# Install PostgreSQL client
#RUN apt-get update && apt-get upgrade -y
#RUN apt-get install libpq-dev -y
#RUN docker-php-ext-install pgsql

# Pre-requirements for installing PHP-MQTT. Installing composer and 7z 
WORKDIR /usr/local/bin
RUN apt-get install p7zip-full -y
COPY ./composer.phar composer
RUN chmod +x composer

# Install PHP-MQTT client. The package requires PHP version 7.4 or higher.
WORKDIR /var/mqtt
RUN composer require php-mqtt/client

# Install PHPMailer. https://github.com/PHPMailer/PHPMailer
WORKDIR /var/PHPMailer
RUN composer require phpmailer/phpmailer

# Copy .bash_aliases and Invoked as an interactive non-login shell
WORKDIR /root
COPY ./bash_aliases .bash_aliases
RUN echo "[ -f ~/.bash_aliases ] && . ~/.bash_aliases" >> /root/.bashrc

# Set workking directory for the webhook server. /var/www/html/ is the default DocumentRoot
WORKDIR /usr/src/mqtt

# Copy only files from www/html
COPY ./usr/src/mqtt/* .

# Start MQTT Subseribe.
CMD [ "php" , "mqtt_subscribe.php" ]
