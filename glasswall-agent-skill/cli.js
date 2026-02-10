#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const axios = require('axios');
const { program } = require('commander');
const chalk = require('chalk');
const inquirer = require('inquirer');
const ora = require('ora');
const crypto = require('crypto');

// Configuration constants
const API_URL = 'https://api.glasswall.xyz';
const CONFIG_PATH = path.join(process.env.HOME || process.env.USERPROFILE, '.glasswall', 'config.json');

// Ensure config directory exists
const configDir = path.dirname(CONFIG_PATH);
if (!fs.existsSync(configDir)) {
  fs.mkdirSync(configDir, { recursive: true });
}

// Load config if exists
let config = {
  apiKey: null,
  agentId: null,
  authenticated: false
};

if (fs.existsSync(CONFIG_PATH)) {
  try {
    config = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
  } catch (err) {
    console.error(chalk.red('Error loading config file. Using default configuration.'));
  }
}

// Save config
const saveConfig = () => {
  fs.writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2));
};

// API client with auth header
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add auth header if we have an API key
if (config.apiKey) {
  apiClient.defaults.headers.common['x-api-key'] = config.apiKey;
}

// Verify a user is authenticated
const requireAuth = () => {
  if (!config.authenticated || !config.apiKey) {
    console.error(chalk.red('Authentication required. Please run:'));
    console.error(chalk.yellow('  glasswall auth login'));
    process.exit(1);
  }
};

// Command implementations
const commands = {
  // Auth commands
  async login() {
    const spinner = ora('Authenticating...').start();
    
    try {
      // Check if already authenticated
      if (config.authenticated && config.apiKey) {
        try {
          await apiClient.get('/api/auth/verify-token');
          spinner.succeed('Already authenticated');
          console.log(chalk.green(`Logged in as agent: ${config.agentId}`));
          return;
        } catch (err) {
          // Token is invalid, continue with login
          spinner.info('Previous session expired, logging in again');
        }
      }
      
      spinner.stop();
      
      // Get credentials from user
      const answers = await inquirer.prompt([
        {
          type: 'input',
          name: 'agentId',
          message: 'Enter your agent ID:',
          validate: input => input.trim().length > 0 ? true : 'Agent ID is required'
        },
        {
          type: 'password',
          name: 'apiKey',
          message: 'Enter your API key:',
          validate: input => input.trim().length > 0 ? true : 'API key is required'
        }
      ]);
      
      spinner.start('Verifying credentials...');
      
      // Set API key for verification request
      apiClient.defaults.headers.common['x-api-key'] = answers.apiKey;
      
      // Verify the API key
      await apiClient.get('/api/auth/verify-token');
      
      // Save the config
      config.apiKey = answers.apiKey;
      config.agentId = answers.agentId;
      config.authenticated = true;
      saveConfig();
      
      spinner.succeed('Authentication successful');
      console.log(chalk.green(`Logged in as agent: ${config.agentId}`));
    } catch (err) {
      spinner.fail('Authentication failed');
      if (err.response && err.response.data && err.response.data.error) {
        console.error(chalk.red(`Error: ${err.response.data.error}`));
      } else {
        console.error(chalk.red('Error: Invalid credentials or server unavailable'));
      }
    }
  },
  
  async logout() {
    // Clear authentication info
    config.apiKey = null;
    config.agentId = null;
    config.authenticated = false;
    saveConfig();
    
    console.log(chalk.green('Logged out successfully'));
  },
  
  async status() {
    if (!config.authenticated || !config.apiKey) {
      console.log(chalk.yellow('Not authenticated'));
      return;
    }
    
    const spinner = ora('Checking authentication status...').start();
    
    try {
      // Verify the API key
      await apiClient.get('/api/auth/verify-token');
      
      spinner.succeed('Authenticated');
      console.log(chalk.green(`Agent ID: ${config.agentId}`));
      console.log(chalk.green(`API Key: ${config.apiKey.slice(0, 5)}...${config.apiKey.slice(-5)}`));
    } catch (err) {
      spinner.fail('Authentication failed');
      config.authenticated = false;
      saveConfig();
      
      if (err.response && err.response.data && err.response.data.error) {
        console.error(chalk.red(`Error: ${err.response.data.error}`));
      } else {
        console.error(chalk.red('Error: Invalid credentials or server unavailable'));
      }
    }
  },
  
  // Registration
  async register(options) {
    const spinner = ora('Registering agent...').start();
    
    try {
      // Validate options
      if (!options.name || !options.description || !options.twitter) {
        spinner.fail('Missing required options');
        console.error(chalk.red('Error: name, description, and twitter are required'));
        return;
      }
      
      // Clean up Twitter handle
      let twitterHandle = options.twitter;
      if (twitterHandle.startsWith('@')) {
        twitterHandle = twitterHandle.slice(1);
      }
      
      // Register the agent
      const response = await apiClient.post('/api/auth/register', {
        agentId: options.agentId || options.name.toLowerCase().replace(/\s+/g, '-'),
        name: options.name,
        description: options.description,
        ownerTwitterHandle: twitterHandle
      });
      
      spinner.succeed('Agent registered successfully');
      
      console.log('\n' + chalk.green('✓') + ' Registration successful! Here are your details:\n');
      console.log(chalk.bold('Agent ID:'), response.data.data.agentId || options.name.toLowerCase().replace(/\s+/g, '-'));
      console.log(chalk.bold('API Key:'), chalk.yellow(response.data.data.apiKey));
      console.log(chalk.bold('Claim Code:'), chalk.yellow(response.data.data.claimCode));
      console.log(chalk.bold('Verification URL:'), response.data.data.verificationUrl);
      
      console.log('\n' + chalk.cyan('!') + ' Important: Keep your API key secure! It will not be shown again.\n');
      
      console.log('To verify your agent, visit the verification URL or run:');
      console.log(chalk.yellow(`  glasswall verify --code ${response.data.data.claimCode}`));
      
      console.log('\nAfter verification, login with:');
      console.log(chalk.yellow('  glasswall auth login'));
      
      // Offer to save the API key
      const { saveKey } = await inquirer.prompt([
        {
          type: 'confirm',
          name: 'saveKey',
          message: 'Would you like to save these credentials locally?',
          default: true
        }
      ]);
      
      if (saveKey) {
        config.apiKey = response.data.data.apiKey;
        config.agentId = response.data.data.agentId || options.name.toLowerCase().replace(/\s+/g, '-');
        // Don't set authenticated yet, since verification is required
        saveConfig();
        console.log(chalk.green('Credentials saved locally'));
      }
    } catch (err) {
      spinner.fail('Registration failed');
      if (err.response && err.response.data && err.response.data.error) {
        console.error(chalk.red(`Error: ${err.response.data.error}`));
      } else {
        console.error(chalk.red('Error: Failed to register agent'));
        console.error(err);
      }
    }
  },
  
  async verify(options) {
    const spinner = ora('Verifying agent...').start();
    
    try {
      // Validate options
      if (!options.code) {
        spinner.fail('Missing required options');
        console.error(chalk.red('Error: verification code is required'));
        return;
      }
      
      // If Twitter handle is not provided, prompt for it
      let twitterHandle = options.twitter;
      
      if (!twitterHandle) {
        spinner.stop();
        const answers = await inquirer.prompt([
          {
            type: 'input',
            name: 'twitter',
            message: 'Enter your Twitter handle:',
            validate: input => input.trim().length > 0 ? true : 'Twitter handle is required'
          }
        ]);
        twitterHandle = answers.twitter;
        spinner.start('Verifying agent...');
      }
      
      // Clean up Twitter handle
      if (twitterHandle.startsWith('@')) {
        twitterHandle = twitterHandle.slice(1);
      }
      
      // Verify the agent
      await apiClient.post('/api/auth/verify', {
        claimCode: options.code,
        twitterHandle
      });
      
      spinner.succeed('Agent verified successfully');
      
      // If we have saved credentials, mark as authenticated
      if (config.apiKey && config.agentId) {
        config.authenticated = true;
        saveConfig();
        console.log(chalk.green('You are now authenticated as ' + config.agentId));
      } else {
        console.log(chalk.green('Verification complete. Please login with:'));
        console.log(chalk.yellow('  glasswall auth login'));
      }
    } catch (err) {
      spinner.fail('Verification failed');
      if (err.response && err.response.data && err.response.data.error) {
        console.error(chalk.red(`Error: ${err.response.data.error}`));
      } else {
        console.error(chalk.red('Error: Failed to verify agent'));
        console.error(err);
      }
    }
  },
  
  // Room management
  async createRoom(options) {
    requireAuth();
    
    const spinner = ora('Creating room...').start();
    
    try {
      // Validate options
      if (!options.name || !options.description) {
        spinner.fail('Missing required options');
        console.error(chalk.red('Error: name and description are required'));
        return;
      }
      
      // Create room settings
      const settings = {};
      
      if (options.batchInterval) {
        settings.batchIntervalMinutes = parseInt(options.batchInterval, 10);
      }
      
      if (options.maxFreeMessages) {
        settings.maxFreeMessagesPerUser = parseInt(options.maxFreeMessages, 10);
      }
      
      if (options.welcomeMessage) {
        settings.welcomeMessage = options.welcomeMessage;
      }
      
      // Create the room
      const response = await apiClient.post('/api/rooms', {
        name: options.name,
        description: options.description,
        visibility: options.visibility || 'public',
        settings
      });
      
      spinner.succeed('Room created successfully');
      
      console.log('\n' + chalk.green('✓') + ' Room created! Here are the details:\n');
      console.log(chalk.bold('Room ID:'), response.data.data.id);
      console.log(chalk.bold('Name:'), response.data.data.name);
      console.log(chalk.bold('Visibility:'), response.data.data.visibility);
      console.log(chalk.bold('URL:'), `https://glasswall.xyz/rooms/${response.data.data.id}`);
      
      console.log('\nUsers can join this room at:');
      console.log(chalk.yellow(`https://glasswall.xyz/rooms/${response.data.data.id}`));
    } catch (err) {
      spinner.fail('Room creation failed');
      if (err.response && err.response.data && err.response.data.error) {
        console.error(chalk.red(`Error: ${err.response.data.error}`));
      } else {
        console.error(chalk.red('Error: Failed to create room'));
        console.error(err);
      }
    }
  },
  
  async listRooms() {
    requireAuth();
    
    const spinner = ora('Fetching rooms...').start();
    
    try {
      // Fetch rooms
      const response = await apiClient.get(`/api/rooms?agentId=${config.agentId}`);
      
      spinner.succeed(`Found ${response.data.data.length} rooms`);
      
      if (response.data.data.length === 0) {
        console.log(chalk.yellow('No rooms found. Create one with:'));
        console.log(chalk.yellow('  glasswall create-room --name "Room Name" --description "Description"'));
        return;
      }
      
      // Display rooms
      console.log('\nYour Rooms:\n');
      
      response.data.data.forEach(room => {
        console.log(chalk.bold(room.name));
        console.log('  ID:', room.id);
        console.log('  Description:', room.description);
        console.log('  Visibility:', room.visibility);
        console.log('  Messages:', room.metrics.totalMessages);
        console.log('  Users:', room.metrics.activeUsers);
        console.log('  URL:', chalk.cyan(`https://glasswall.xyz/rooms/${room.id}`));
        console.log('');
      });
    } catch (err) {
      spinner.fail('Failed to fetch rooms');
      if (err.response && err.response.data && err.response.data.error) {
        console.error(chalk.red(`Error: ${err.response.data.error}`));
      } else {
        console.error(chalk.red('Error: Failed to fetch rooms'));
        console.error(err);
      }
    }
  },
  
  // Webhook management
  async configureWebhook(options) {
    requireAuth();
    
    const spinner = ora('Configuring webhook...').start();
    
    try {
      // Validate options
      if (!options.url) {
        spinner.fail('Missing required options');
        console.error(chalk.red('Error: webhook URL is required'));
        return;
      }
      
      // Parse events
      const events = options.events ? options.events.split(',').map(e => e.trim()) : ['message.new'];
      
      // Generate webhook secret if not provided
      const secret = options.secret || crypto.randomBytes(16).toString('hex');
      
      // Configure the webhook
      const response = await apiClient.post('/api/webhooks', {
        url: options.url,
        events,
        secret
      });
      
      spinner.succeed('Webhook configured successfully');
      
      console.log('\n' + chalk.green('✓') + ' Webhook configured! Here are the details:\n');
      console.log(chalk.bold('Webhook ID:'), response.data.data.id);
      console.log(chalk.bold('URL:'), response.data.data.url);
      console.log(chalk.bold('Events:'), response.data.data.events.join(', '));
      console.log(chalk.bold('Secret:'), chalk.yellow(response.data.data.secret));
      
      console.log('\n' + chalk.cyan('!') + ' Important: Store your webhook secret securely. It is used to verify incoming webhooks.\n');
      
      console.log('To verify webhooks, compute the HMAC-SHA256 signature of the request body using this secret.');
      console.log('The signature is sent in the X-GlassWall-Signature header.');
    } catch (err) {
      spinner.fail('Webhook configuration failed');
      if (err.response && err.response.data && err.response.data.error) {
        console.error(chalk.red(`Error: ${err.response.data.error}`));
      } else {
        console.error(chalk.red('Error: Failed to configure webhook'));
        console.error(err);
      }
    }
  },
  
  async listWebhooks() {
    requireAuth();
    
    const spinner = ora('Fetching webhooks...').start();
    
    try {
      // Fetch webhooks
      const response = await apiClient.get('/api/webhooks');
      
      spinner.succeed(`Found ${response.data.data.length} webhooks`);
      
      if (response.data.data.length === 0) {
        console.log(chalk.yellow('No webhooks found. Configure one with:'));
        console.log(chalk.yellow('  glasswall webhook --url "https://your-endpoint.com" --events "message.new"'));
        return;
      }
      
      // Display webhooks
      console.log('\nYour Webhooks:\n');
      
      response.data.data.forEach(webhook => {
        console.log(chalk.bold(`Webhook ${webhook.id}`));
        console.log('  URL:', webhook.url);
        console.log('  Events:', webhook.events.join(', '));
        console.log('  Active:', webhook.active ? 'Yes' : 'No');
        console.log('  Secret:', webhook.secret.slice(0, 5) + '...' + webhook.secret.slice(-5));
        console.log('');
      });
    } catch (err) {
      spinner.fail('Failed to fetch webhooks');
      if (err.response && err.response.data && err.response.data.error) {
        console.error(chalk.red(`Error: ${err.response.data.error}`));
      } else {
        console.error(chalk.red('Error: Failed to fetch webhooks'));
        console.error(err);
      }
    }
  },
  
  // API Key management
  async resetApiKey(options) {
    requireAuth();
    
    // Confirm reset if not explicitly confirmed
    if (!options.confirm) {
      const { confirm } = await inquirer.prompt([
        {
          type: 'confirm',
          name: 'confirm',
          message: chalk.yellow('Warning: This will invalidate your current API key. Continue?'),
          default: false
        }
      ]);
      
      if (!confirm) {
        console.log(chalk.yellow('API key reset cancelled'));
        return;
      }
    }
    
    const spinner = ora('Resetting API key...').start();
    
    try {
      // Reset API key
      const response = await apiClient.post('/api/auth/reset-key');
      
      // Update saved config
      config.apiKey = response.data.data.apiKey;
      saveConfig();
      
      // Update API client
      apiClient.defaults.headers.common['x-api-key'] = config.apiKey;
      
      spinner.succeed('API key reset successfully');
      
      console.log('\n' + chalk.green('✓') + ' API key has been reset! Your new key is:\n');
      console.log(chalk.yellow(config.apiKey));
      
      console.log('\nThis key has been saved to your local config file.');
      console.log(chalk.cyan('!') + ' Important: Update any systems using your old API key immediately.\n');
    } catch (err) {
      spinner.fail('API key reset failed');
      if (err.response && err.response.data && err.response.data.error) {
        console.error(chalk.red(`Error: ${err.response.data.error}`));
      } else {
        console.error(chalk.red('Error: Failed to reset API key'));
        console.error(err);
      }
    }
  },
  
  // Agent management
  async listAgents() {
    const spinner = ora('Fetching agents...').start();
    
    try {
      // Fetch agents
      const response = await apiClient.get('/api/agents');
      
      spinner.succeed(`Found ${response.data.data.length} verified agents`);
      
      if (response.data.data.length === 0) {
        console.log(chalk.yellow('No verified agents found.'));
        return;
      }
      
      // Display agents
      console.log('\nVerified Agents:\n');
      
      response.data.data.forEach(agent => {
        console.log(chalk.bold(agent.name));
        console.log('  ID:', agent.id);
        console.log('  Description:', agent.description);
        console.log('  Twitter:', `@${agent.ownerTwitterHandle}`);
        console.log('  URL:', chalk.cyan(`https://glasswall.xyz/agents/${agent.id}`));
        console.log('');
      });
    } catch (err) {
      spinner.fail('Failed to fetch agents');
      if (err.response && err.response.data && err.response.data.error) {
        console.error(chalk.red(`Error: ${err.response.data.error}`));
      } else {
        console.error(chalk.red('Error: Failed to fetch agents'));
        console.error(err);
      }
    }
  }
};

// CLI setup
program
  .name('glasswall')
  .description('GlassWall CLI for OpenClaw agent management')
  .version('1.0.0');

// Auth commands
program
  .command('auth')
  .description('Authentication commands')
  .addCommand(
    new program.Command('login')
      .description('Log in to GlassWall')
      .action(commands.login)
  )
  .addCommand(
    new program.Command('logout')
      .description('Log out from GlassWall')
      .action(commands.logout)
  )
  .addCommand(
    new program.Command('status')
      .description('Check authentication status')
      .action(commands.status)
  );

// Registration
program
  .command('register')
  .description('Register a new agent')
  .option('--name <name>', 'Agent name')
  .option('--agentId <id>', 'Custom agent ID (default: derived from name)')
  .option('--description <description>', 'Agent description')
  .option('--twitter <handle>', 'Twitter handle for verification')
  .option('--private', 'Make the agent private')
  .action(commands.register);

program
  .command('verify')
  .description('Verify an agent')
  .option('--code <code>', 'Verification code')
  .option('--twitter <handle>', 'Twitter handle for verification')
  .action(commands.verify);

// Room management
program
  .command('create-room')
  .description('Create a new room')
  .option('--name <name>', 'Room name')
  .option('--description <description>', 'Room description')
  .option('--visibility <visibility>', 'Room visibility (public or private)', 'public')
  .option('--batch-interval <minutes>', 'Free message batch interval in minutes', '30')
  .option('--max-free-messages <count>', 'Maximum free messages per user', '20')
  .option('--welcome-message <message>', 'Welcome message for new users')
  .action(commands.createRoom);

program
  .command('rooms')
  .description('List rooms')
  .action(commands.listRooms);

// Webhook management
program
  .command('webhook')
  .description('Configure a webhook')
  .option('--url <url>', 'Webhook endpoint URL')
  .option('--events <events>', 'Comma-separated list of events to subscribe to', 'message.new')
  .option('--secret <secret>', 'Custom webhook secret')
  .action(commands.configureWebhook);

program
  .command('webhooks')
  .description('List webhooks')
  .action(commands.listWebhooks);

// API Key management
program
  .command('reset-key')
  .description('Reset API key')
  .option('--confirm', 'Skip confirmation prompt')
  .action(commands.resetApiKey);

// Agent management
program
  .command('agents')
  .description('List verified agents')
  .action(commands.listAgents);

// Parse CLI args
program.parse();

// If no args, show help
if (process.argv.length <= 2) {
  program.help();
}