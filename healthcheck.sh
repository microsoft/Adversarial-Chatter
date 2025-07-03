#!/bin/sh

# Check Web App (Angular)
curl --fail http://localhost:4000 || exit 1

# Check API Server (Node.js)
curl --fail http://localhost:3000 || exit 1
