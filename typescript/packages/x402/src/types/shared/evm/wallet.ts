import { createPublicClient, createWalletClient, http, publicActions } from "viem";
import type {
  Chain,
  Transport,
  Client,
  Account,
  RpcSchema,
  PublicActions,
  WalletActions,
  PublicClient,
} from "viem";
import {
  baseSepolia,
  avalancheFuji,
  sei,
  seiTestnet,
} from "viem/chains";
import { privateKeyToAccount, type LocalAccount } from "viem/accounts";
import { Hex } from "viem";

/**
 * Wallet client with signing + public actions
 */
export type SignerWallet<
  chain extends Chain = Chain,
  transport extends Transport = Transport,
  account extends Account = Account,
> = Client<
  transport,
  chain,
  account,
  RpcSchema,
  PublicActions<transport, chain, account> & WalletActions<chain, account>
>;

/**
 * Read-only public client
 */
export type ConnectedClient<
  transport extends Transport = Transport,
  chain extends Chain | undefined = Chain,
  account extends Account | undefined = undefined,
> = PublicClient<transport, chain, account>;

/**
 * Base Sepolia public client
 */
export function createClientSepolia(): ConnectedClient<
  Transport,
  typeof baseSepolia,
  undefined
> {
  return createPublicClient({
    chain: baseSepolia,
    transport: http(),
  }).extend(publicActions);
}

/**
 * Avalanche Fuji public client
 */
export function createClientAvalancheFuji(): ConnectedClient<
  Transport,
  typeof avalancheFuji,
  undefined
> {
  return createPublicClient({
    chain: avalancheFuji,
    transport: http(),
  }).extend(publicActions);
}

/**
 * Base Sepolia signer
 */
export function createSignerSepolia(privateKey: Hex): SignerWallet<typeof baseSepolia> {
  return createWalletClient({
    chain: baseSepolia,
    transport: http(),
    account: privateKeyToAccount(privateKey),
  }).extend(publicActions);
}

/**
 * Avalanche Fuji signer
 */
export function createSignerAvalancheFuji(
  privateKey: Hex,
): SignerWallet<typeof avalancheFuji> {
  return createWalletClient({
    chain: avalancheFuji,
    transport: http(),
    account: privateKeyToAccount(privateKey),
  }).extend(publicActions);
}

/**
 * Sei testnet signer
 */
export function createSignerSeiTestnet(
  privateKey: Hex,
): SignerWallet<typeof seiTestnet> {
  return createWalletClient({
    chain: seiTestnet,
    transport: http(),
    account: privateKeyToAccount(privateKey),
  }).extend(publicActions);
}

/**
 * Sei mainnet signer
 */
export function createSignerSei(privateKey: Hex): SignerWallet<typeof sei> {
  return createWalletClient({
    chain: sei,
    transport: http(),
    account: privateKeyToAccount(privateKey),
  }).extend(publicActions);
}

/**
 * Type guard: is this a signer wallet
 */
export function isSignerWallet<
  TChain extends Chain = Chain,
  TTransport extends Transport = Transport,
  TAccount extends Account = Account,
>(
  wallet: SignerWallet<TChain, TTransport, TAccount> | Account,
): wallet is SignerWallet<TChain, TTransport, TAccount> {
  return typeof wallet === "object" && wallet !== null && "chain" in wallet && "transport" in wallet;
}

/**
 * Type guard: is this a LocalAccount (real signing account)
 *
 * IMPORTANT:
 * This matches viem's actual LocalAccount contract:
 * address + full signing surface
 */
export function isAccount<
  TChain extends Chain = Chain,
  TTransport extends Transport = Transport,
  TAccount extends Account = Account,
>(
  wallet: SignerWallet<TChain, TTransport, TAccount> | LocalAccount,
): wallet is LocalAccount {
  const w = wallet as LocalAccount;

  return (
    typeof wallet === "object" &&
    wallet !== null &&
    typeof w.address === "string" &&
    typeof w.type === "string" &&
    typeof w.sign === "function" &&
    typeof w.signMessage === "function" &&
    typeof w.signTypedData === "function" &&
    typeof w.signTransaction === "function"
  );
}
