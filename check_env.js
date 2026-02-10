const fs = require('fs');
const path = require('path');
const homeDir = require('os').homedir();
const envFile = path.join(homeDir, '.openclaw', '.env');

console.log('Checking environment variables for OpenClaw Gateway');
console.log('Current environment:');
console.log(`BRAVE_API_KEY: ${process.env.BRAVE_API_KEY || '(not set)'}`);

// Check if .env file exists
if (fs.existsSync(envFile)) {
  console.log(`\nContent of ${envFile}:`);
  console.log(fs.readFileSync(envFile, 'utf8'));
} else {
  console.log(`\n${envFile} does not exist`);
}

// Check gateway.env
const gatewayEnv = path.join(homeDir, '.openclaw', 'gateway.env');
if (fs.existsSync(gatewayEnv)) {
  console.log(`\nContent of ${gatewayEnv}:`);
  console.log(fs.readFileSync(gatewayEnv, 'utf8'));
} else {
  console.log(`\n${gatewayEnv} does not exist`);
}

// Check openclaw.json for web section
const configFile = path.join(homeDir, '.openclaw', 'openclaw.json');
if (fs.existsSync(configFile)) {
  try {
    const config = JSON.parse(fs.readFileSync(configFile, 'utf8'));
    console.log('\nWeb section in openclaw.json:');
    console.log(config.web || '(not present)');
  } catch (error) {
    console.log(`\nError reading openclaw.json: ${error.message}`);
  }
} else {
  console.log(`\n${configFile} does not exist`);
}

// Check web.json
const webConfigFile = path.join(homeDir, '.openclaw', 'config', 'web.json');
if (fs.existsSync(webConfigFile)) {
  try {
    console.log(`\nContent of ${webConfigFile}:`);
    console.log(fs.readFileSync(webConfigFile, 'utf8'));
  } catch (error) {
    console.log(`\nError reading web.json: ${error.message}`);
  }
} else {
  console.log(`\n${webConfigFile} does not exist`);
}