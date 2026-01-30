# =================================================================================
# PROYECTO: PlanIA - PHP Container
# ARCHIVO: Dockerfile.php
# COPYRIGHT: © 2026 Fondo Thoth AC.
# =================================================================================

FROM php:8.2-apache

# Install PHP extensions
RUN docker-php-ext-install pdo pdo_mysql mysqli

# Enable Apache modules
RUN a2enmod rewrite headers

# Configure Apache document root
ENV APACHE_DOCUMENT_ROOT /var/www/html/public
RUN sed -ri -e 's!/var/www/html!${APACHE_DOCUMENT_ROOT}!g' /etc/apache2/sites-available/*.conf
RUN sed -ri -e 's!/var/www/!${APACHE_DOCUMENT_ROOT}!g' /etc/apache2/apache2.conf /etc/apache2/conf-available/*.conf

# Allow .htaccess overrides
RUN sed -i '/<Directory \/var\/www\/>/,/<\/Directory>/ s/AllowOverride None/AllowOverride All/' /etc/apache2/apache2.conf

# Set working directory
WORKDIR /var/www/html

# Copy application files
COPY public/ /var/www/html/public/
COPY config/ /var/www/html/config/
COPY views/ /var/www/html/views/

# Set permissions
RUN chown -R www-data:www-data /var/www/html

EXPOSE 80
