# GlassWall Vercel Deployment Guide

This guide provides instructions for managing and troubleshooting Vercel deployments for the GlassWall application.

## Deployment Configuration

The GlassWall application is configured for Vercel deployment with:

1. **Next.js Framework**: Optimized for server-side rendering and static site generation
2. **Vercel Integration**: Automatic deployments on commits to the main branch and PR previews
3. **Environment Variables**: Configured in the Vercel dashboard and vercel.json

## Key Configuration Files

- **`vercel.json`**: Contains deployment configuration, environment variables, and routing rules
- **`next.config.js`**: Next.js specific configuration including build options and optimization settings

## Common Deployment Issues

### 404 DEPLOYMENT_NOT_FOUND Error

This typically occurs when:

1. The deployment has been deleted from Vercel
2. The branch or PR was closed/merged without proper redirection
3. There's a configuration issue in the Vercel project settings

### Solution Steps

1. **Update vercel.json**: Ensure the correct framework is specified and routing is properly configured
   ```json
   {
     "version": 2,
     "framework": "nextjs",
     "rewrites": [
       { "source": "/(.*)", "destination": "/" }
     ]
   }
   ```

2. **Fix next.config.js**: Add output optimization and routing improvements
   ```javascript
   /** @type {import('next').NextConfig} */
   const nextConfig = {
     // Your existing config...
     output: 'standalone',
     trailingSlash: false,
   }
   ```

3. **Check Vercel Project Settings**:
   - Go to Vercel project settings -> General -> Build & Development Settings
   - Select "Next.js" for Framework Preset (not "Other")
   - Verify the correct root directory is specified
   - Check that environment variables are properly set

4. **Force Redeploy**: Use the `force_deploy.py` script to trigger a new deployment if necessary

## Deployment Monitoring

Two scripts are available for monitoring and managing deployments:

1. **`verify_deployment.py`**: Checks if a deployment is accessible and returns status information
   ```bash
   python verify_deployment.py [project-name]
   ```

2. **`force_deploy.py`**: Triggers a manual deployment to Vercel
   ```bash
   python force_deploy.py [project-directory]
   ```

## Troubleshooting Steps

1. **Check logs**: Review build and runtime logs in the Vercel dashboard
2. **Verify configuration**: Ensure vercel.json and next.config.js are properly configured
3. **Test locally**: Run `next build` and `next start` locally to verify the build process
4. **Check dependencies**: Ensure all dependencies are correctly specified in package.json
5. **Review routes**: Verify that all routes are properly configured in vercel.json

## Best Practices

1. **Automated Testing**: Run tests before deployment to catch issues early
2. **Progressive Deployments**: Use Vercel's preview deployments for testing before production
3. **Environment Variables**: Keep sensitive information in Vercel's environment variables
4. **Monitoring**: Regularly check deployment status and performance
5. **Caching Strategy**: Implement effective caching for optimal performance

## Recommended Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Next.js Deployment Guide](https://nextjs.org/docs/deployment)
- [Troubleshooting Vercel Deployments](https://vercel.com/guides/why-is-my-deployed-project-giving-404)