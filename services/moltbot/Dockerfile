# ============================================
# MOLTBOT + OSINT CONTAINER - Alpine (Ligero)
# ============================================
# Contenedor compacto (~500MB):
# - Alpine Linux (ARM64 nativo)
# - Node.js 22
# - Chromium
# - Moltbot + OSINT tools
# ============================================

FROM node:22-alpine

# Instalar dependencias
RUN apk add --no-cache \
    bash \
    curl \
    wget \
    git \
    python3 \
    py3-pip \
    chromium \
    nss \
    freetype \
    harfbuzz \
    ca-certificates \
    ttf-freefont \
    && rm -rf /var/cache/apk/*

# Instalar herramientas OSINT (Python)
RUN pip3 install --no-cache-dir --break-system-packages \
    sherlock-project \
    dnspython \
    requests \
    beautifulsoup4 \
    whois

# Instalar Moltbot
COPY package.json ./
RUN npm install

COPY server.js ./

# Salud del contenedor
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8080/ || exit 1

EXPOSE 8080

CMD ["npm", "start"]
