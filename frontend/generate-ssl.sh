#!/bin/bash

# Generate SSL certificates for localhost development
echo "🔐 Generating SSL certificates for localhost..."

# Generate private key
openssl genrsa -out localhost-key.pem 2048

# Generate certificate signing request
openssl req -new -key localhost-key.pem -out localhost.csr -subj "/C=US/ST=CA/L=San Francisco/O=Development/CN=localhost"

# Generate self-signed certificate
openssl x509 -req -in localhost.csr -signkey localhost-key.pem -out localhost.pem -days 365

# Clean up CSR file
rm localhost.csr

echo "✅ SSL certificates generated:"
echo "   - localhost-key.pem (private key)"
echo "   - localhost.pem (certificate)"
echo ""
echo "🚀 You can now run: npm run dev:https"
echo ""
echo "⚠️  Your browser will show a security warning for self-signed certificates."
echo "   Click 'Advanced' -> 'Proceed to localhost (unsafe)' to continue."
