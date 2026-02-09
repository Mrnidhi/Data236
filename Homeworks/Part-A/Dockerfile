# HW1 Blog Submission Form - Docker Container
# Uses Nginx to serve static HTML/JS files

# Base image: nginx on Alpine Linux (lightweight, ~5MB)
FROM nginx:alpine

# Remove default Nginx welcome page
RUN rm -rf /usr/share/nginx/html/*

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy our custom nginx config
COPY nginx.conf /etc/nginx/conf.d/

# Copy the HTML and JS files
COPY hw1-SrinidhiGowda.html /usr/share/nginx/html/hw1.html
COPY hw1-SrinidhiGowda.js /usr/share/nginx/html/hw1-SrinidhiGowda.js

# Expose port 80 for HTTP traffic
EXPOSE 80

# Start Nginx in foreground mode
CMD ["nginx", "-g", "daemon off;"]