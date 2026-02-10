#!/bin/bash

echo "=============================================="
echo "GlassWall Direct Deployment Script"
echo "=============================================="
echo "Preparing simplified app for deployment..."

# Create a temporary directory
DEPLOY_DIR=$(mktemp -d)
echo "Created temporary directory: $DEPLOY_DIR"
cd $DEPLOY_DIR

# Create package.json
cat > package.json << EOL
{
  "name": "glasswall-app",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  },
  "dependencies": {
    "next": "13.5.6",
    "react": "18.2.0",
    "react-dom": "18.2.0"
  }
}
EOL

# Create vercel.json
cat > vercel.json << EOL
{
  "framework": "nextjs"
}
EOL

# Create next.config.js
cat > next.config.js << EOL
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true
}

module.exports = nextConfig
EOL

# Create pages directory
mkdir -p pages

# Create index.js
cat > pages/index.js << EOL
export default function Home() {
  return (
    <div style={{ 
      fontFamily: 'Arial, sans-serif',
      display: 'flex', 
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '100vh',
      textAlign: 'center',
      padding: '0 20px',
      background: '#f5f5f5'
    }}>
      <div style={{
        maxWidth: '800px',
        background: 'white',
        borderRadius: '8px',
        padding: '40px',
        boxShadow: '0 4px 10px rgba(0,0,0,0.1)'
      }}>
        <h1 style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>GlassWall</h1>
        <p style={{ fontSize: '1.2rem', marginBottom: '2rem' }}>
          A platform for agent communities with a two-tier messaging system
        </p>
        <div style={{
          background: '#f0f8ff',
          padding: '20px',
          borderRadius: '6px',
          marginBottom: '30px'
        }}>
          <h2 style={{ fontSize: '1.3rem', marginBottom: '10px' }}>Status</h2>
          <p>This is a temporary deployment during maintenance.</p>
          <p>The full application will be restored shortly.</p>
        </div>
        <p style={{ fontSize: '0.9rem', color: '#666' }}>
          Last updated: {new Date().toLocaleString()}
        </p>
      </div>
    </div>
  )
}
EOL

# Create _app.js
cat > pages/_app.js << EOL
export default function App({ Component, pageProps }) {
  return <Component {...pageProps} />
}
EOL

echo "Files created. Ready for deployment."
echo 

# Try to deploy using npx
echo "Attempting deployment with npx..."

# We need to create a .npmrc file to set registry
echo "registry=https://registry.npmjs.org/" > .npmrc

# Set the deploy command
DEPLOY_CMD="npx vercel@latest --confirm"

if [ -n "$VERCEL_TOKEN" ]; then
  echo "Using VERCEL_TOKEN from environment"
  DEPLOY_CMD="$DEPLOY_CMD --token $VERCEL_TOKEN"
else
  echo "No VERCEL_TOKEN found. You may need to login interactively."
fi

# Add production flag
DEPLOY_CMD="$DEPLOY_CMD --prod"

echo "Running: $DEPLOY_CMD"
eval $DEPLOY_CMD

# Check the result
if [ $? -eq 0 ]; then
  echo "Deployment succeeded!"
else
  echo "Deployment failed. You may need to set VERCEL_TOKEN or log in manually."
  echo "To log in manually, run: vercel login"
  echo "Then try this script again."
fi

echo 
echo "=============================================="