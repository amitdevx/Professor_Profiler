#!/bin/bash
set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Installing Professor Profiler CLI...${NC}"

# Check node
if ! command -v node &> /dev/null; then
  echo 'Error: Node.js is required. Install from https://nodejs.org'
  exit 1
fi

# Change to the cli directory
cd "$(dirname "$0")"

# Install deps
npm install

# Build
npm run build

# Install globally
npm run install:global

echo -e "${GREEN} Professor Profiler CLI installed successfully!${NC}"
echo -e "${GREEN} You can now use 'prof' from anywhere.${NC}"
echo ""
echo -e "${BLUE}To enable autocomplete in your shell, add this to your ~/.bashrc or ~/.zshrc:${NC}"
echo "    eval \"\$(prof completion)\""
echo ""
echo "Try: prof --help"
