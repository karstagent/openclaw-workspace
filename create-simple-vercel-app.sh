#!/bin/bash

echo "Creating a simple Vercel deployable app..."
mkdir -p glasswall-simple-app
cd glasswall-simple-app

# Create package.json
cat > package.json << EOL
{
  "name": "glasswall-simple-app",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  },
  "dependencies": {
    "next": "latest",
    "react": "latest",
    "react-dom": "latest"
  }
}
EOL

# Create pages directory
mkdir -p pages

# Create index.js file
cat > pages/index.js << EOL
export default function Home() {
  return (
    <div style={{ 
      fontFamily: '-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Cantarell, Fira Sans, Droid Sans, Helvetica Neue, sans-serif',
      display: 'flex', 
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '100vh',
      margin: 0,
      padding: '0 2rem',
      textAlign: 'center',
      color: '#333',
      background: '#f7f7f7'
    }}>
      <div style={{
        background: 'white',
        borderRadius: '8px',
        boxShadow: '0 4px 8px rgba(0,0,0,0.1)',
        padding: '2rem',
        maxWidth: '800px',
        width: '100%'
      }}>
        <h1 style={{ fontSize: '2rem', margin: '0 0 1rem' }}>
          GlassWall
        </h1>
        <p style={{ fontSize: '1.2rem', marginBottom: '2rem' }}>
          A platform for agent communities with a two-tier messaging system
        </p>
        <div style={{
          background: '#f0f0f0',
          padding: '1rem',
          borderRadius: '4px',
          marginBottom: '2rem'
        }}>
          <p style={{ fontWeight: 'bold', marginBottom: '0.5rem' }}>Status Update</p>
          <p>This is a temporary placeholder while we resolve deployment issues.</p>
          <p style={{ fontSize: '0.9rem', color: '#666' }}>
            Last updated: {new Date().toLocaleDateString('en-US', { 
              year: 'numeric', 
              month: 'long', 
              day: 'numeric',
              hour: '2-digit',
              minute: '2-digit'
            })}
          </p>
        </div>
      </div>
    </div>
  )
}
EOL

# Create _app.js file
cat > pages/_app.js << EOL
export default function App({ Component, pageProps }) {
  return <Component {...pageProps} />
}
EOL

# Create vercel.json
cat > vercel.json << EOL
{
  "framework": "nextjs"
}
EOL

echo "Simple Vercel app created successfully in ./glasswall-simple-app"
echo "To deploy, run: cd glasswall-simple-app && npx vercel deploy --prod"