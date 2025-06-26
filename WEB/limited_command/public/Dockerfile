FROM php:8.2-apache

RUN apt-get update && \
    apt-get install -y \
        libcurl4-openssl-dev \
        unzip \
        git \
        zip && \
    docker-php-ext-install curl

COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

WORKDIR /var/www/html

COPY ./flag.txt /flag.txt

COPY ./src /var/www/html

RUN chown -R www-data:www-data /var/www/html

RUN composer require symfony/process