# Build stage
FROM node:16-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY . .
RUN npm run build

# Production stage - Use Node.js to serve static files
FROM node:16-alpine

WORKDIR /app

# Install serve package to serve static files
RUN npm install -g serve

# Copy built files from build stage
COPY --from=build /app/build ./build

EXPOSE 80

# Use serve to host the static files
CMD ["serve", "-s", "build", "-l", "80"]
