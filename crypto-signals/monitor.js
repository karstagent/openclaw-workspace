#!/usr/bin/env node

const https = require('https');
const fs = require('fs');

// Load config
const config = JSON.parse(fs.readFileSync('./config.json', 'utf8'));

// Track sent signals to avoid duplicates
const sentTokens = new Set();

async function fetchJSON(url) {
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch (e) {
          reject(e);
        }
      });
    }).on('error', reject);
  });
}

async function sendSignal(message) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({ message });
    const options = {
      hostname: 'glasswall.xyz',
      port: 443,
      path: '/api/agents/reply',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Agent-Token': config.glasswall.agentToken,
        'Content-Length': data.length
      }
    };

    const req = https.request(options, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(JSON.parse(body || '{}'));
        } else {
          reject(new Error(`HTTP ${res.statusCode}: ${body}`));
        }
      });
    });

    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

async function checkNewTokens() {
  try {
    // Fetch trending tokens from Dexscreener (free API)
    const url = 'https://api.dexscreener.com/latest/dex/tokens/trending';
    const data = await fetchJSON(url);

    if (!data || !data.pairs) {
      console.log('[Monitor] No pairs data');
      return;
    }

    // Filter for Base chain
    const basePairs = data.pairs.filter(p => 
      p.chainId === 'base' && 
      p.liquidity?.usd >= config.monitoring.minLiquidityUSD &&
      p.volume?.h24 >= config.monitoring.minVolumeUSD
    );

    console.log(`[Monitor] Found ${basePairs.length} Base pairs meeting criteria`);

    for (const pair of basePairs.slice(0, 3)) {  // Top 3 only
      const tokenAddr = pair.baseToken.address;
      
      if (sentTokens.has(tokenAddr)) {
        continue; // Already sent signal for this token
      }

      // Check if token is less than 24 hours old
      const pairAge = Date.now() - pair.pairCreatedAt;
      const hoursOld = pairAge / (1000 * 60 * 60);

      if (hoursOld > 24) {
        continue; // Too old
      }

      // Format signal
      const signal = formatSignal(pair, hoursOld);
      
      console.log(`[Signal] Sending for ${pair.baseToken.symbol}`);
      await sendSignal(signal);
      
      sentTokens.add(tokenAddr);
      
      // Wait between signals
      await new Promise(r => setTimeout(r, 2000));
    }

  } catch (error) {
    console.error('[Monitor] Error:', error.message);
  }
}

function formatSignal(pair, hoursOld) {
  const priceChange = pair.priceChange?.h24 || 0;
  const emoji = priceChange > 0 ? '🚀' : '📉';
  
  return `${emoji} **NEW TOKEN ALERT**

**${pair.baseToken.name}** (${pair.baseToken.symbol})
Contract: \`${pair.baseToken.address}\`

💰 Price: $${parseFloat(pair.priceUsd).toFixed(8)}
📊 24h Change: ${priceChange > 0 ? '+' : ''}${priceChange.toFixed(2)}%
💧 Liquidity: $${formatNumber(pair.liquidity.usd)}
📈 Volume (24h): $${formatNumber(pair.volume.h24)}
⏰ Age: ${hoursOld.toFixed(1)} hours

🔗 [Trade on ${pair.dexId}](${pair.url})

⚠️ DYOR - This is not financial advice`;
}

function formatNumber(num) {
  if (num >= 1e6) return (num / 1e6).toFixed(2) + 'M';
  if (num >= 1e3) return (num / 1e3).toFixed(2) + 'K';
  return num.toFixed(2);
}

// Main loop
console.log('[CryptoSignals] Starting monitor...');
console.log('[CryptoSignals] Chatroom:', config.glasswall.chatroomUrl);

// Send startup message
sendSignal('🤖 **CryptoSignals Bot is now online!**\n\nMonitoring Base chain for hot new tokens. Signals will be sent here as paid messages ($0.10 each).\n\nStay tuned for alpha! 🚀')
  .then(() => console.log('[Startup] Welcome message sent'))
  .catch(e => console.error('[Startup] Failed:', e.message));

// Check immediately, then every interval
checkNewTokens();
setInterval(checkNewTokens, config.monitoring.checkIntervalSeconds * 1000);

console.log(`[Monitor] Checking every ${config.monitoring.checkIntervalSeconds}s`);
