#!/bin/bash

# Rebranding script: Suna -> agentiK, Kortix -> agentiK

echo "Starting rebranding process..."

# Find and replace "Suna" with "agentiK" (case-sensitive)
find . -type f \( -name "*.js" -o -name "*.jsx" -o -name "*.ts" -o -name "*.tsx" -o -name "*.py" -o -name "*.json" -o -name "*.md" -o -name "*.html" -o -name "*.yaml" -o -name "*.yml" \) \
  -not -path "*/node_modules/*" -not -path "*/.git/*" -not -path "*/dist/*" -not -path "*/build/*" \
  -exec sed -i 's/Suna/agentiK/g' {} +

# Find and replace "suna" with "agentik" (lowercase)
find . -type f \( -name "*.js" -o -name "*.jsx" -o -name "*.ts" -o -name "*.tsx" -o -name "*.py" -o -name "*.json" -o -name "*.md" -o -name "*.html" -o -name "*.yaml" -o -name "*.yml" \) \
  -not -path "*/node_modules/*" -not -path "*/.git/*" -not -path "*/dist/*" -not -path "*/build/*" \
  -exec sed -i 's/suna/agentik/g' {} +

# Find and replace "SUNA" with "AGENTIK" (uppercase)
find . -type f \( -name "*.js" -o -name "*.jsx" -o -name "*.ts" -o -name "*.tsx" -o -name "*.py" -o -name "*.json" -o -name "*.md" -o -name "*.html" -o -name "*.yaml" -o -name "*.yml" \) \
  -not -path "*/node_modules/*" -not -path "*/.git/*" -not -path "*/dist/*" -not -path "*/build/*" \
  -exec sed -i 's/SUNA/AGENTIK/g' {} +

# Find and replace "Kortix" with "agentiK"
find . -type f \( -name "*.js" -o -name "*.jsx" -o -name "*.ts" -o -name "*.tsx" -o -name "*.py" -o -name "*.json" -o -name "*.md" -o -name "*.html" -o -name "*.yaml" -o -name "*.yml" \) \
  -not -path "*/node_modules/*" -not -path "*/.git/*" -not -path "*/dist/*" -not -path "*/build/*" \
  -exec sed -i 's/Kortix/agentiK/g' {} +

# Find and replace "kortix" with "agentik" (lowercase)
find . -type f \( -name "*.js" -o -name "*.jsx" -o -name "*.ts" -o -name "*.tsx" -o -name "*.py" -o -name "*.json" -o -name "*.md" -o -name "*.html" -o -name "*.yaml" -o -name "*.yml" \) \
  -not -path "*/node_modules/*" -not -path "*/.git/*" -not -path "*/dist/*" -not -path "*/build/*" \
  -exec sed -i 's/kortix/agentik/g' {} +

echo "Rebranding complete!"
