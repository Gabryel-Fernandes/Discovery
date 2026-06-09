FROM node:20-alpine

WORKDIR /app

# copia dependências primeiro
COPY package.json package-lock.json ./

RUN npm install

# copia o resto do projeto
COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]