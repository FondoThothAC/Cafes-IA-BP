FROM node:22-alpine

WORKDIR /app

# Install docker CLI for exec commands to moltbot
RUN apk add --no-cache docker-cli

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3002

CMD ["node", "server.js"]
