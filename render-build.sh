#!/bin/bash

# This script is used to install necessary libraries for Playwright to run WebKit

# Update package lists
echo "Updating package lists..."
apt-get update

# Install necessary libraries for Playwright
echo "Installing necessary libraries..."
apt-get install -y \
    libgstreamer-gl1.0-0 \
    libgstreamer-plugins-bad1.0-0 \
    libenchant-2-2 \
    libsecret-1-0 \
    libmanette-0.2-0 \
    libgles2-mesa

# Clean up to reduce image size
echo "Cleaning up..."
apt-get clean
rm -rf /var/lib/apt/lists/*

echo "All necessary libraries have been installed successfully."
