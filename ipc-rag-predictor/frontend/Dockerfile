FROM node:18-bullseye-slim

WORKDIR /app

# Install deps
COPY package.json package-lock.json ./
# Use npm install to avoid issues with lockfile/platform mismatches in CI
RUN npm install --silent --no-audit --no-fund

# Copy source
COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
