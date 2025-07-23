# Frontend Dockerfile for envacare_project
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package.json and install dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of the application code
COPY . .

# Build the frontend
RUN npm run build

# Install serve to run the production build
RUN npm install -g serve

# Expose port
EXPOSE 3000

# Start the frontend using serve
CMD ["serve", "-s", "dist", "-l", "3000"]
