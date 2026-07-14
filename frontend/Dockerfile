FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 5173

# Start Vite dev server exposing host
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
