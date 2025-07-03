# -------- Stage 1: Build Angular Frontend --------
FROM node:23.3.0 AS glitchyweb

WORKDIR /app/glitchyweb

# Copy frontend source code
COPY GlitchyWeb/ ./

# Install the application dependencies
RUN cd GlitchyWeb && npm install

# Run the Angular  server and API server
RUN cd GlitchyWeb && npx ng serve

RUN cd GlitchyWeb/server && npx ng serve

# -------- Stage 2: Python Backend + Final Image --------
FROM python:3.10 AS advchat

WORKDIR /app

# Copy backend source code
COPY ADV_CHAT/ ./ADV_CHAT/

# Create and activate virtual environment, install dependencies
RUN python -m venv venv && \
    ./venv/bin/pip install --upgrade pip && \
    ./venv/bin/pip install -r ADV_CHAT/requirements.txt

RUN apt-get update && \
    apt-get install -y unixodbc unixodbc-dev

# Install Azure Developer CLI
RUN curl -fsSL https://aka.ms/install-azd.sh | bash

# # Copy built frontend from previous stage (optional, if needed by backend)
# COPY --from=glitchyweb /app/web/dist/ ./frontend/

# Copy health check script
COPY healthcheck.sh /usr/local/bin/healthcheck.sh
RUN chmod +x /usr/local/bin/healthcheck.sh

HEALTHCHECK --interval=10s --timeout=5s --retries=3 CMD /usr/local/bin/healthcheck.sh

# Expose ports (adjust as needed)
EXPOSE 3000 4000

# Run backend script
CMD ["./venv/bin/python", "ADV_CHAT/SocialAgent.py"]
