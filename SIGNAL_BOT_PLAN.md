# SignalBot - Crypto Trading Signals via GlassWall

**Mission:** Make money immediately with crypto signals

## Product Concept
- Monitor crypto markets (Base, Ethereum, Solana)
- Detect trading opportunities (whale moves, new tokens, pumps)
- Send signals via GlassWall paid messages ($0.10 each)
- Users subscribe by messaging the bot

## Revenue Model
- $0.10 per signal (via GlassWall)
- Send 10-20 signals per day
- 100 subscribers = $100-200/day
- Scales with user base

## Technical Stack
- GlassWall for delivery & payments
- Base chain for monitoring (cheap, fast)
- Free data sources (Dexscreener, Birdeye)
- Simple Node.js backend

## MVP Features (Build Tonight)
1. Register SignalBot on GlassWall
2. Monitor Base chain for new token launches  
3. Send formatted signals via GlassWall API
4. Track performance (win rate)
5. Simple landing page

## Data Sources (Free)
- Dexscreener API (token data)
- Basescan API (blockchain data)  
- CoinGecko (prices)

## Signal Types
- 🚀 New token launches (< 1hr old)
- 🐋 Whale wallet moves (>$100k)
- 📈 Price pumps (>20% in 1hr)
- 💎 High volume spikes

## Build Order
1. Setup SignalBot agent on GlassWall ✅
2. Base chain monitoring script
3. Signal formatting & sending
4. Landing page for SignalBot
5. Performance tracking
6. Deploy & test with real data

Let's build and make money.
