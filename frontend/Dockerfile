FROM node:25-slim

WORKDIR /app/frontend

COPY . /app/frontend

WORKDIR /app/frontend/codebase-agent

RUN npm install

EXPOSE 3000

CMD ["npm", "run", "dev"]
