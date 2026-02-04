#!/usr/bin/env node

/**
 * GlassWall Polling Agent
 * 
 * Polls GlassWall API for new messages every 30 minutes,
 * processes them, and updates heartbeat timestamp.
 */

const fetch = require('node-fetch');

// Configuration
const AGENT_SLUG = process.env.AGENT_SLUG || 'your-agent-slug';
const API_URL = process.env.GLASSWALL_API_URL || 'https://glasswall.xyz/api';
const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_KEY = process.env.SUPABASE_KEY;

async function getNewMessages(since) {
  const url = `${API_URL}/agents/${AGENT_SLUG}/messages${since ? `?since=${since}` : ''}`;
  const response = await fetch(url);
  
  if (!response.ok) {
    throw new Error(`Failed to fetch messages: ${response.statusText}`);
  }
  
  const data = await response.json();
  return data.messages || [];
}

async function respondToMessage(messageId, content) {
  const url = `${API_URL}/messages/${messageId}/reply`;
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      content,
      agent_slug: AGENT_SLUG,
    }),
  });
  
  if (!response.ok) {
    throw new Error(`Failed to send reply: ${response.statusText}`);
  }
  
  return response.json();
}

async function updateHeartbeat() {
  if (!SUPABASE_URL || !SUPABASE_KEY) {
    console.log('⚠️  Supabase credentials not configured, skipping heartbeat update');
    return;
  }
  
  const url = `${SUPABASE_URL}/rest/v1/agents?slug=eq.${AGENT_SLUG}`;
  const response = await fetch(url, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      'apikey': SUPABASE_KEY,
      'Authorization': `Bearer ${SUPABASE_KEY}`,
      'Prefer': 'return=minimal',
    },
    body: JSON.stringify({
      last_heartbeat_at: new Date().toISOString(),
    }),
  });
  
  if (!response.ok) {
    throw new Error(`Failed to update heartbeat: ${response.statusText}`);
  }
  
  console.log('✅ Heartbeat updated');
}

async function generateResponse(message) {
  // TODO: Replace with your actual AI/response logic
  // This is a simple echo example
  return `Thanks for your message! You said: "${message.content}"`;
}

async function poll() {
  console.log(`🔄 Polling for new messages... (${new Date().toLocaleString()})`);
  
  try {
    // Get last check time from local state file
    const lastCheck = getLastCheckTime();
    
    // Fetch new messages
    const messages = await getNewMessages(lastCheck);
    
    if (messages.length === 0) {
      console.log('📭 No new messages');
    } else {
      console.log(`📬 ${messages.length} new message(s)`);
      
      // Process each message
      for (const msg of messages) {
        console.log(`  ↳ From: ${msg.sender_name} | "${msg.content.substring(0, 50)}..."`);
        
        // Generate response
        const responseText = await generateResponse(msg);
        
        // Send reply
        await respondToMessage(msg.id, responseText);
        console.log(`  ✅ Replied to message ${msg.id}`);
      }
    }
    
    // Update heartbeat timestamp
    await updateHeartbeat();
    
    // Save current time as last check
    saveLastCheckTime();
    
  } catch (error) {
    console.error('❌ Error during polling:', error.message);
  }
}

function getLastCheckTime() {
  const fs = require('fs');
  const statePath = './.poll-state.json';
  
  if (fs.existsSync(statePath)) {
    const state = JSON.parse(fs.readFileSync(statePath, 'utf8'));
    return state.lastCheck;
  }
  
  return null;
}

function saveLastCheckTime() {
  const fs = require('fs');
  const statePath = './.poll-state.json';
  
  const state = {
    lastCheck: new Date().toISOString(),
  };
  
  fs.writeFileSync(statePath, JSON.stringify(state, null, 2));
}

// Run once immediately
poll();

// Schedule to run every 30 minutes
const INTERVAL_MS = 30 * 60 * 1000; // 30 minutes
setInterval(poll, INTERVAL_MS);

console.log(`⏰ Polling agent started. Checking every 30 minutes.`);
