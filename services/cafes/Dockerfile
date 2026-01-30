# Dockerfile for CAFES (PHP 8.2 + Apache)
FROM php:8.2-apache

# Install extensions
RUN docker-php-ext-install mysqli pdo pdo_mysql

# Enable headers module for CORS/Auth
RUN a2enmod headers rewrite

# Set working directory
WORKDIR /var/www/html

# Copy source code
COPY . /var/www/html/

# Permissions
RUN chown -R www-data:www-data /var/www/html \
    && chmod -R 755 /var/www/html

# Expose port (Internal 80, mapped to 8081 in compose)
EXPOSE 80
