#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// Path to OpenClaw config
const configPath = '/Users/karst/.openclaw/openclaw.json';

// Read current config
try {
  const configFile = fs.readFileSync(configPath, 'utf8');
  const config = JSON.parse(configFile);
  console.log('Successfully read OpenClaw config file');

  // Create backup
  const backupPath = path.join(path.dirname(configPath), 'openclaw.backup.json');
  fs.writeFileSync(backupPath, configFile);
  console.log(`Created backup at ${backupPath}`);

  // Add automation settings
  if (!config.agents.defaults.heartbeat) {
    config.agents.defaults.heartbeat = {};
  }

  // Set heartbeat settings
  config.agents.defaults.heartbeat.enabled = true;
  config.agents.defaults.heartbeat.intervalMinutes = 30;
  config.agents.defaults.heartbeat.prompt = "Read HEARTBEAT.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK.";

  // Add autostart
  config.agents.defaults.autostart = true;

  // Add automation section
  if (!config.agents.defaults.automation) {
    config.agents.defaults.automation = {};
  }
  
  // Configure automation settings
  config.agents.defaults.automation = {
    enabled: true,
    autonomousTasks: true,
    backgroundProcesses: {
      enabled: true,
      maxConcurrent: 3,
      restartOnFailure: true,
      scripts: [
        "persistent_runner.py",
        "github_sync.py",
        "monitor.py"
      ]
    },
    scheduledRuns: [
      {
        name: "DailyUpdate",
        schedule: "0 9 * * *",
        prompt: "Generate a daily progress update on all current projects. Include status, blockers, and next steps.",
        model: "openrouter/anthropic/claude-3.7-sonnet",
        deliver: true
      },
      {
        name: "WeeklyReview",
        schedule: "0 10 * * 1",
        prompt: "Create a comprehensive weekly review of all projects, including metrics, achievements, and strategic recommendations for the coming week.",
        model: "openrouter/anthropic/claude-3.7-sonnet",
        deliver: true
      },
      {
        name: "SystemCheck",
        schedule: "*/30 * * * *",
        prompt: "Check all system processes and logs for errors or warnings. Report any issues found.",
        model: "openrouter/deepseek/deepseek-coder",
        deliver: false,
        saveToFile: "/Users/karst/.openclaw/workspace/logs/system_check.log"
      }
    ],
    modelSelection: {
      enabled: true,
      rules: [
        {
          pattern: "administrative|simple|check|status",
          model: "openrouter/deepseek/deepseek-coder"
        },
        {
          pattern: "strategic|complex|analysis|research",
          model: "openrouter/anthropic/claude-3.7-sonnet"
        },
        {
          default: "openrouter/anthropic/claude-3.5-haiku"
        }
      ]
    },
    workflowMonitor: {
      enabled: true,
      checkIntervalMinutes: 5,
      scriptPath: "/Users/karst/.openclaw/workspace/ensure_workflow_running.sh"
    }
  };

  // Configure subagent autoSpawn
  if (!config.agents.defaults.subagents.autoSpawn) {
    config.agents.defaults.subagents.autoSpawn = {};
  }

  config.agents.defaults.subagents.autoSpawn = {
    enabled: true,
    thresholdTasks: 3,
    defaultModel: "openrouter/anthropic/claude-3.5-haiku"
  };

  // Update meta information
  config.meta.lastTouchedAt = new Date().toISOString();
  
  // Write updated config
  fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
  console.log('Successfully updated OpenClaw config with automation settings');

} catch (error) {
  console.error('Error updating OpenClaw config:', error);
}