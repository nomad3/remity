# Use an official Node runtime as a parent image
# Use a version known to be compatible with react-scripts 5
FROM node:18-alpine

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json (if available)
# Copying these first leverages Docker cache
COPY package*.json ./

# Install dependencies
# Use --force if encountering peer dependency issues with older react-scripts versions
RUN npm install

# Copy the rest of the application code
COPY . .

# React app runs on port 3000
EXPOSE 3000

# Default command to start the development server
CMD ["npm", "start"]
