#!/bin/bash

# This script checks for potential secrets left in the codebase.
# It searches for specific keys that should have been moved to the secrets repo.

echo "Running Secret Lint..."

ERRORS=0

check_pattern() {
  local pattern="$1"
  local description="$2"

  echo "Checking for $description..."
  # Grep for pattern and exclude known safe patterns
  matches=$(grep -rE "$pattern" kubernetes \
    | grep -v "charts/" \
    | grep -v "will be overriden" \
    | grep -v '""' \
    | grep -v "#" \
    | grep -v "\.svc\.cluster\.local" \
    | grep -v "127.0.0.1" \
    | grep -v "github.com")

  if [ ! -z "$matches" ]; then
    echo "❌ Found potential $description leaks:"
    echo "$matches"
    ERRORS=1
  else
    echo "✅ No $description found."
  fi
}

# Check for passwords that are not empty or placeholders
# We look for 'password:' followed by something that is NOT just whitespace or empty quotes
check_pattern "password:\s+(\"([^\"]+)\"|[^[:space:]\"]+)" "passwords"

# Check for secrets
check_pattern "secret:\s+(\"([^\"]+)\"|[^[:space:]\"]+)" "secrets"

# Check for tokens
check_pattern "token:\s+(\"([^\"]+)\"|[^[:space:]\"]+)" "tokens"

# Check for ingress hosts that are not empty
# Pattern searches for 'host: ' followed by non-space/quote chars
# We exclude internal k8s hosts in the grep filter above
check_pattern "host:\s+([a-zA-Z0-9][a-zA-Z0-9.-]+)" "Ingress hosts"

if [ $ERRORS -eq 1 ]; then
  echo "⚠️  Potential secrets found! Please review the output above."
  exit 1
else
  echo "🎉 No obvious secrets found!"
  exit 0
fi
