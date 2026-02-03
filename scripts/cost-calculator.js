#!/usr/bin/env node
/**
 * Cost Calculator - Track token usage and costs across sessions
 * 
 * Usage:
 *   node cost-calculator.js                 # Show current month
 *   node cost-calculator.js --all           # Show all time
 *   node cost-calculator.js --session KEY   # Show specific session
 */

const fs = require('fs');
const path = require('path');

// Model pricing (per 1M tokens)
const PRICING = {
  'anthropic/claude-opus-4': { input: 15, output: 75 },
  'anthropic/claude-sonnet-4': { input: 3, output: 15 },
  'anthropic/claude-sonnet-4-5': { input: 3, output: 15 },
  'anthropic/claude-haiku-4': { input: 0.25, output: 1.25 },
};

const MONTHLY_BUDGET = 200;

function calculateCost(inputTokens, outputTokens, model) {
  const pricing = PRICING[model] || { input: 3, output: 15 }; // Default to Sonnet
  const inputCost = (inputTokens / 1000000) * pricing.input;
  const outputCost = (outputTokens / 1000000) * pricing.output;
  return inputCost + outputCost;
}

function formatCost(cost) {
  return `$${cost.toFixed(2)}`;
}

function formatTokens(tokens) {
  if (tokens >= 1000000) return `${(tokens / 1000000).toFixed(2)}M`;
  if (tokens >= 1000) return `${(tokens / 1000).toFixed(1)}k`;
  return tokens.toString();
}

function getSessionStats() {
  const agentsDir = path.join(process.env.HOME, '.openclaw', 'agents', 'main', 'sessions');
  
  if (!fs.existsSync(agentsDir)) {
    console.error('Sessions directory not found');
    return [];
  }

  const sessionFiles = fs.readdirSync(agentsDir).filter(f => f.endsWith('.jsonl'));
  
  const stats = [];
  
  for (const file of sessionFiles) {
    const filePath = path.join(agentsDir, file);
    const lines = fs.readFileSync(filePath, 'utf8').split('\n').filter(Boolean);
    
    let inputTokens = 0;
    let outputTokens = 0;
    let model = 'anthropic/claude-sonnet-4-5';
    let startTime = null;
    let endTime = null;
    
    for (const line of lines) {
      try {
        const msg = JSON.parse(line);
        
        if (msg.usage) {
          inputTokens += msg.usage.input_tokens || 0;
          outputTokens += msg.usage.output_tokens || 0;
        }
        
        if (msg.model) {
          model = msg.model;
        }
        
        const timestamp = new Date(msg.timestamp || msg.created_at);
        if (!startTime || timestamp < startTime) startTime = timestamp;
        if (!endTime || timestamp > endTime) endTime = timestamp;
        
      } catch (e) {
        // Skip invalid lines
      }
    }
    
    if (inputTokens > 0 || outputTokens > 0) {
      stats.push({
        sessionId: path.basename(file, '.jsonl'),
        inputTokens,
        outputTokens,
        totalTokens: inputTokens + outputTokens,
        model,
        cost: calculateCost(inputTokens, outputTokens, model),
        startTime,
        endTime,
      });
    }
  }
  
  return stats;
}

function main() {
  const args = process.argv.slice(2);
  const showAll = args.includes('--all');
  const sessionKey = args.find(a => a.startsWith('--session='))?.split('=')[1];
  
  console.log('📊 Token Usage & Cost Report\n');
  
  const stats = getSessionStats();
  
  if (stats.length === 0) {
    console.log('No session data found.');
    return;
  }
  
  // Filter by current month unless --all
  const now = new Date();
  const filtered = showAll ? stats : stats.filter(s => {
    return s.startTime && 
           s.startTime.getMonth() === now.getMonth() && 
           s.startTime.getFullYear() === now.getFullYear();
  });
  
  // Calculate totals
  const totalInput = filtered.reduce((sum, s) => sum + s.inputTokens, 0);
  const totalOutput = filtered.reduce((sum, s) => sum + s.outputTokens, 0);
  const totalCost = filtered.reduce((sum, s) => sum + s.cost, 0);
  
  console.log(`Period: ${showAll ? 'All Time' : 'Current Month'}`);
  console.log(`Sessions: ${filtered.length}`);
  console.log(`Input tokens: ${formatTokens(totalInput)}`);
  console.log(`Output tokens: ${formatTokens(totalOutput)}`);
  console.log(`Total tokens: ${formatTokens(totalInput + totalOutput)}`);
  console.log(`Total cost: ${formatCost(totalCost)}`);
  console.log(`Budget remaining: ${formatCost(MONTHLY_BUDGET - totalCost)} / ${formatCost(MONTHLY_BUDGET)}`);
  console.log(`Budget used: ${((totalCost / MONTHLY_BUDGET) * 100).toFixed(1)}%`);
  
  // Alert if over threshold
  if (totalCost > MONTHLY_BUDGET * 0.75) {
    console.log('\n⚠️  WARNING: Over 75% of monthly budget!');
  } else if (totalCost > MONTHLY_BUDGET * 0.5) {
    console.log('\n⚠️  NOTICE: Over 50% of monthly budget');
  }
  
  // Show top sessions by cost
  if (filtered.length > 1) {
    console.log('\n📈 Top Sessions by Cost:');
    const sorted = [...filtered].sort((a, b) => b.cost - a.cost).slice(0, 5);
    sorted.forEach((s, i) => {
      const date = s.startTime ? s.startTime.toLocaleDateString() : 'unknown';
      console.log(`${i + 1}. ${date} - ${formatTokens(s.totalTokens)} tokens - ${formatCost(s.cost)}`);
    });
  }
}

if (require.main === module) {
  main();
}

module.exports = { calculateCost, getSessionStats };
