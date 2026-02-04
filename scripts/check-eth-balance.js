#!/usr/bin/env node

const { createPublicClient, http } = require('viem');
const { base } = require('viem/chains');

const MY_ADDRESS = '0x81032e30b7A44bBBd3007c9cEc67ebD8b220D9A8';

async function main() {
  const client = createPublicClient({
    chain: base,
    transport: http(),
  });

  const balance = await client.getBalance({ address: MY_ADDRESS });
  const balanceInETH = Number(balance) / 1e18;
  console.log(`ETH: ${balanceInETH}`);
  console.log(`Wei: ${balance}`);
}

main().catch(console.error);
