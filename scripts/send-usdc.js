#!/usr/bin/env node

const { createWalletClient, http, parseUnits } = require('viem');
const { privateKeyToAccount } = require('viem/accounts');
const { base } = require('viem/chains');

// Configuration
const PRIVATE_KEY = '0x98cf3b1c69044265f2b7b042b7cad5f198047a5df6f263b09a1c85a10ccb4845';
const USDC_ADDRESS = '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913'; // USDC on Base
const TO_ADDRESS = '0x40Fd5434C515Db16701ae0589F48D6182a426566';
const AMOUNT = '0.10'; // 0.10 USDC

// ERC20 transfer ABI
const ERC20_ABI = [
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
  // Create account from private key
  const account = privateKeyToAccount(PRIVATE_KEY);
  
  // Create wallet client
  const client = createWalletClient({
    account,
    chain: base,
    transport: http(),
  });

  console.log(`Sending ${AMOUNT} USDC from ${account.address} to ${TO_ADDRESS}...`);

  // Convert amount to proper decimals (USDC has 6 decimals)
  const amountInSmallestUnit = parseUnits(AMOUNT, 6);

  // Send transaction
  const hash = await client.writeContract({
    address: USDC_ADDRESS,
    abi: ERC20_ABI,
    functionName: 'transfer',
    args: [TO_ADDRESS, amountInSmallestUnit],
  });

  console.log(`Transaction sent: ${hash}`);
  console.log(`View on BaseScan: https://basescan.org/tx/${hash}`);
}

main().catch(console.error);
