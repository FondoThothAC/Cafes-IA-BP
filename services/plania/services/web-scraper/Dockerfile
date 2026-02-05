FROM ghcr.io/puppeteer/puppeteer:21.5.0

USER root
WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Copy app source
COPY . .

# Create directory for screenshots/audit
RUN mkdir -p public/screenshots knowledge_base && \
    chown -R pptruser:pptruser public knowledge_base audit.sqlite || true

# Switch back to non-root user
USER pptruser

# Environment variables
ENV PORT=3005
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/google-chrome-stable

EXPOSE 3005

CMD ["node", "server.js"]
