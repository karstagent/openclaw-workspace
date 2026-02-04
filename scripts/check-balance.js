#!/usr/bin/env node

const { createPublicClient, http } = require('viem');
const { base } = require('viem/chains');

const USDC_ADDRESS = '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913';
const MY_ADDRESS = '0x81032e30b7A44bBBd3007c9cEc67ebD8b220D9A8';

const ERC20_ABI = [
  {
    name: 'balanceOf',
    type: 'function',
    stateMutability: 'view',
    inputs: [{ name: 'account', type: 'address' }],
    outputs: [{ type: 'uint256' }],
  },
];

async function main() {
  const client = createPublicClient({
    chain: base,
    transport: http(),
  });

  const balance = await client.readContract({
    address: USDC_ADDRESS,
    abi: ERC20_ABI,
    functionName: 'balanceOf',
    args: [MY_ADDRESS],
  });

  // USDC has 6 decimals
  const balanceInUSDC = Number(balance) / 1_000_000;
  console.log(balanceInUSDC);
}

main().catch(console.error);
