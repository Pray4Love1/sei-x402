import { spawnSync } from "node:child_process";

type Account = {
  name: string;
  flag: string;
};

const accounts: Record<string, Account> = {
  alice: { name: "Alice", flag: "--alice" },
  bob: { name: "Bob", flag: "--bob" },
  charlie: { name: "Charlie", flag: "--charlie" },
  relayer: { name: "Relayer", flag: "--relayer" },
};

const nodePath = process.env.NODE_PATH ?? "./target/release/node-template";
const dryRun = process.argv.includes("--dry-run");

const runCommand = (command: string[]): void => {
  console.log(`$ ${command.join(" ")}`);
  if (dryRun) {
    return;
  }
  const result = spawnSync(command[0], command.slice(1), {
    stdio: "inherit",
  });
  if (result.status !== 0) {
    throw new Error(`Command failed: ${command.join(" ")}`);
  }
};

const nodeExtrinsic = (account: Account, call: string): void => {
  runCommand([nodePath, "--dev", account.flag, "--", "extrinsic", call]);
};

const nodeRpc = (account: Account, call: string): void => {
  runCommand([nodePath, "--dev", account.flag, "--", "rpc", call]);
};

const main = (): void => {
  console.log("Step 1 — Environment variables");
  console.log(`NODE_PATH=${nodePath}`);
  console.log("ALICE=//Alice BOB=//Bob CHARLIE=//Charlie RELAYER=//Relayer");

  console.log("\nStep 2 — Register identities");
  nodeExtrinsic(accounts.alice, "GenZk402.register_identity(H256::from_low_u64_be(1))");
  nodeExtrinsic(accounts.bob, "GenZk402.register_identity(H256::from_low_u64_be(2))");
  nodeExtrinsic(
    accounts.charlie,
    "GenZk402.register_identity(H256::from_low_u64_be(3))",
  );

  console.log("\nStep 3 — Create wallets");
  nodeExtrinsic(
    accounts.alice,
    "GenZk402.create_wallet(H256::from_low_u64_be(101), vec![Bob,Charlie], 500)",
  );
  nodeExtrinsic(
    accounts.bob,
    "GenZk402.create_wallet(H256::from_low_u64_be(102), vec![Alice,Charlie], 500)",
  );
  nodeExtrinsic(
    accounts.charlie,
    "GenZk402.create_wallet(H256::from_low_u64_be(103), vec![Alice,Bob], 500)",
  );

  console.log("\nStep 4 — Deposit funds");
  nodeExtrinsic(accounts.alice, "GenZk402.deposit(1000)");
  nodeExtrinsic(accounts.bob, "GenZk402.deposit(1000)");
  nodeExtrinsic(accounts.charlie, "GenZk402.deposit(1000)");

  console.log("\nStep 5 — Send payments");
  nodeExtrinsic(
    accounts.alice,
    "GenZk402.send_payment(Bob, 50, H256::from_low_u64_be(101))",
  );
  nodeExtrinsic(
    accounts.bob,
    "GenZk402.send_payment(Charlie, 30, H256::from_low_u64_be(102))",
  );

  console.log("\nStep 6 — Initiate recovery");
  nodeExtrinsic(
    accounts.charlie,
    "GenZk402.initiate_recovery(Alice, H256::from_low_u64_be(201))",
  );

  console.log("\nStep 7 — Approve recovery");
  const recoveryId = "<recovery_id_from_previous_step>";
  nodeExtrinsic(accounts.bob, `GenZk402.approve_recovery(${recoveryId})`);
  nodeExtrinsic(accounts.charlie, `GenZk402.approve_recovery(${recoveryId})`);

  console.log("\nStep 8 — Withdraw funds with PIN");
  nodeExtrinsic(
    accounts.alice,
    "GenZk402.withdraw(100, H256::from_low_u64_be(201))",
  );

  console.log("\nStep 9 — Gasless transaction relay");
  const signedPayload = "<signed_payload>";
  nodeExtrinsic(
    accounts.relayer,
    `GenZk402.relay_transaction(Alice, Charlie, 50, Nonces::get(Alice), ${signedPayload})`,
  );

  console.log("\nStep 10 — Verify events");
  nodeRpc(accounts.alice, "state_getStorage('System.Events')");
};

main();
