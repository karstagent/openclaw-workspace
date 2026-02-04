#!/usr/bin/env node

const { createWalletClient, createPublicClient, http } = require('viem');
const { privateKeyToAccount } = require('viem/accounts');
const { base } = require('viem/chains');

// Configuration
const PRIVATE_KEY = '0x98cf3b1c69044265f2b7b042b7cad5f198047a5df6f263b09a1c85a10ccb4845';
const USDC_ADDRESS = '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913';
const TO_ADDRESS = '0x40Fd5434C515Db16701ae0589F48D6182a426566';
const MY_ADDRESS = '0x81032e30b7A44bBBd3007c9cEc67ebD8b220D9A8';

// ERC20 ABI
const ERC20_ABI = [
  {
    name: 'balanceOf',
    type: 'function',
    stateMutability: 'view',
    inputs: [{ name: 'account', type: 'address' }],
    outputs: [{ type: 'uint256' }],
  },
  {
    name: 'transfer',
    type: 'function',
    stateMutability: 'nonpayable',
    inputs: [
      { name: 'to', type: 'address' },
      { name: 'amount', type: 'uint256' },
    ],
    outputs: [{ type: 'bool' }],
  },
];

async function main() {
  // Create clients
  const publicClient = createPublicClient({
    chain: base,
    transport: http(),
  });

  const account = privateKeyToAccount(PRIVATE_KEY);
  const walletClient = createWalletClient({
    account,
    chain: base,
    transport: http(),
  });

  // Get current balance
  const balance = await publicClient.readContract({
    address: USDC_ADDRESS,
    abi: ERC20_ABI,
    functionName: 'balanceOf',
    args: [MY_ADDRESS],
  });

  const balanceInUSDC = Number(balance) / 1_000_000;
  console.log(`Current balance: ${balanceInUSDC} USDC`);

  if (balance === 0n) {
    console.log('No USDC to send');
    return;
  }

  console.log(`Sending ${balanceInUSDC} USDC to ${TO_ADDRESS}...`);

  // Send all USDC
  const hash = await walletClient.writeContract({
    address: USDC_ADDRESS,
    abi: ERC20_ABI,
    functionName: 'transfer',
    args: [TO_ADDRESS, balance],
  });

  console.log(`Transaction sent: ${hash}`);
  console.log(`View on BaseScan: https://basescan.org/tx/${hash}`);
}

main().catch(console.error);
