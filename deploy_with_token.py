#!/usr/bin/env python3
import os
import sys
import subprocess
import requests
import json
from datetime import datetime

def log_message(message, level="INFO"):
    """Log a message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

def create_vercel_json():
    """Create a simplified vercel.json file"""
    vercel_json = {
        "framework": "nextjs"
    }
    
    # Write to file
    with open('vercel.json', 'w') as f:
        json.dump(vercel_json, f, indent=2)
    
    log_message("Created vercel.json with simplified configuration")

def create_package_json():
    """Create a minimal package.json file"""
    package_json = {
        "name": "glasswall-app",
        "version": "0.1.0",
        "private": True,
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
    
    # Write to file
    with open('package.json', 'w') as f:
        json.dump(package_json, f, indent=2)
    
    log_message("Created package.json with minimal dependencies")

def create_next_config():
    """Create a basic next.config.js file"""
    next_config = """
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
}

module.exports = nextConfig
"""
    
    # Write to file
    with open('next.config.js', 'w') as f:
        f.write(next_config)
    
    log_message("Created next.config.js with basic configuration")

def create_pages():
    """Create basic pages directory with index.js"""
    # Create pages directory if it doesn't exist
    os.makedirs('pages', exist_ok=True)
    
    # Create index.js
    index_js = """
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
"""
    
    # Write index.js
    with open('pages/index.js', 'w') as f:
        f.write(index_js)
    
    # Create _app.js
    app_js = """
export default function App({ Component, pageProps }) {
  return <Component {...pageProps} />
}
"""
    
    # Write _app.js
    with open('pages/_app.js', 'w') as f:
        f.write(app_js)
    
    log_message("Created pages directory with index.js and _app.js")

def deploy_to_vercel(token=None):
    """Deploy to Vercel using CLI with token if provided"""
    if not token:
        log_message("No token provided, skipping deployment", "WARNING")
        return False
    
    # Set environment variable for token
    os.environ['VERCEL_TOKEN'] = token
    
    # Run Vercel CLI with token
    try:
        log_message("Deploying to Vercel...")
        result = subprocess.run(
            ["vercel", "--token", token, "--prod", "--confirm"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.returncode == 0:
            log_message("Deployment successful!")
            log_message(f"Output: {result.stdout}")
            return True
        else:
            log_message(f"Deployment failed: {result.stderr}", "ERROR")
            return False
    except Exception as e:
        log_message(f"Error during deployment: {str(e)}", "ERROR")
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("GlassWall Emergency Deployment Script")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Create a directory for the simplified app
    app_dir = os.path.expanduser("~/glasswall-emergency-app")
    os.makedirs(app_dir, exist_ok=True)
    os.chdir(app_dir)
    
    log_message(f"Working in directory: {app_dir}")
    
    # Create the files needed
    create_vercel_json()
    create_package_json()
    create_next_config()
    create_pages()
    
    # Check for Vercel token
    token = os.environ.get('VERCEL_TOKEN')
    if not token:
        log_message("No VERCEL_TOKEN found in environment", "WARNING")
        log_message("You need to set VERCEL_TOKEN environment variable for deployment")
        log_message("Or enter a token now:")
        token = input("Vercel token: ").strip()
    
    # Deploy to Vercel if we have a token
    if token:
        success = deploy_to_vercel(token)
        if success:
            log_message("Emergency deployment completed successfully")
            return 0
        else:
            log_message("Emergency deployment failed", "ERROR")
            return 1
    else:
        log_message("No token provided, cannot deploy", "ERROR")
        return 1

if __name__ == "__main__":
    sys.exit(main())