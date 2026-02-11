package main

import (
	"flag"
	"fmt"
	"os"
	"os/exec"
	"strings"
)

type account struct {
	name string
	flag string
}

var accounts = map[string]account{
	"alice":   {name: "Alice", flag: "--alice"},
	"bob":     {name: "Bob", flag: "--bob"},
	"charlie": {name: "Charlie", flag: "--charlie"},
	"relayer": {name: "Relayer", flag: "--relayer"},
}

func runCommand(command []string, dryRun bool) error {
	fmt.Printf("$ %s\n", strings.Join(command, " "))
	if dryRun {
		return nil
	}
	cmd := exec.Command(command[0], command[1:]...)
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	return cmd.Run()
}

func nodeExtrinsic(nodePath string, acct account, call string, dryRun bool) error {
	command := []string{nodePath, "--dev", acct.flag, "--", "extrinsic", call}
	return runCommand(command, dryRun)
}

func nodeRPC(nodePath string, acct account, call string, dryRun bool) error {
	command := []string{nodePath, "--dev", acct.flag, "--", "rpc", call}
	return runCommand(command, dryRun)
}

func main() {
	dryRun := flag.Bool("dry-run", false, "Print commands without executing them")
	flag.Parse()

	nodePath := os.Getenv("NODE_PATH")
	if nodePath == "" {
		nodePath = "./target/release/node-template"
	}

	fmt.Println("Step 1 — Environment variables")
	fmt.Printf("NODE_PATH=%s\n", nodePath)
	fmt.Println("ALICE=//Alice BOB=//Bob CHARLIE=//Charlie RELAYER=//Relayer")

	fmt.Println("\nStep 2 — Register identities")
	if err := nodeExtrinsic(nodePath, accounts["alice"], "GenZk402.register_identity(H256::from_low_u64_be(1))", *dryRun); err != nil {
		panic(err)
	}
	if err := nodeExtrinsic(nodePath, accounts["bob"], "GenZk402.register_identity(H256::from_low_u64_be(2))", *dryRun); err != nil {
		panic(err)
	}
	if err := nodeExtrinsic(nodePath, accounts["charlie"], "GenZk402.register_identity(H256::from_low_u64_be(3))", *dryRun); err != nil {
		panic(err)
	}

	fmt.Println("\nStep 3 — Create wallets")
	if err := nodeExtrinsic(nodePath, accounts["alice"], "GenZk402.create_wallet(H256::from_low_u64_be(101), vec![Bob,Charlie], 500)", *dryRun); err != nil {
		panic(err)
	}
	if err := nodeExtrinsic(nodePath, accounts["bob"], "GenZk402.create_wallet(H256::from_low_u64_be(102), vec![Alice,Charlie], 500)", *dryRun); err != nil {
		panic(err)
	}
	if err := nodeExtrinsic(nodePath, accounts["charlie"], "GenZk402.create_wallet(H256::from_low_u64_be(103), vec![Alice,Bob], 500)", *dryRun); err != nil {
		panic(err)
	}

	fmt.Println("\nStep 4 — Deposit funds")
	if err := nodeExtrinsic(nodePath, accounts["alice"], "GenZk402.deposit(1000)", *dryRun); err != nil {
		panic(err)
	}
	if err := nodeExtrinsic(nodePath, accounts["bob"], "GenZk402.deposit(1000)", *dryRun); err != nil {
		panic(err)
	}
	if err := nodeExtrinsic(nodePath, accounts["charlie"], "GenZk402.deposit(1000)", *dryRun); err != nil {
		panic(err)
	}

	fmt.Println("\nStep 5 — Send payments")
	if err := nodeExtrinsic(nodePath, accounts["alice"], "GenZk402.send_payment(Bob, 50, H256::from_low_u64_be(101))", *dryRun); err != nil {
		panic(err)
	}
	if err := nodeExtrinsic(nodePath, accounts["bob"], "GenZk402.send_payment(Charlie, 30, H256::from_low_u64_be(102))", *dryRun); err != nil {
		panic(err)
	}

	fmt.Println("\nStep 6 — Initiate recovery")
	if err := nodeExtrinsic(nodePath, accounts["charlie"], "GenZk402.initiate_recovery(Alice, H256::from_low_u64_be(201))", *dryRun); err != nil {
		panic(err)
	}

	fmt.Println("\nStep 7 — Approve recovery")
	recoveryID := "<recovery_id_from_previous_step>"
	if err := nodeExtrinsic(nodePath, accounts["bob"], fmt.Sprintf("GenZk402.approve_recovery(%s)", recoveryID), *dryRun); err != nil {
		panic(err)
	}
	if err := nodeExtrinsic(nodePath, accounts["charlie"], fmt.Sprintf("GenZk402.approve_recovery(%s)", recoveryID), *dryRun); err != nil {
		panic(err)
	}

	fmt.Println("\nStep 8 — Withdraw funds with PIN")
	if err := nodeExtrinsic(nodePath, accounts["alice"], "GenZk402.withdraw(100, H256::from_low_u64_be(201))", *dryRun); err != nil {
		panic(err)
	}

	fmt.Println("\nStep 9 — Gasless transaction relay")
	signedPayload := "<signed_payload>"
	relayCall := "GenZk402.relay_transaction(Alice, Charlie, 50, Nonces::get(Alice), " + signedPayload + ")"
	if err := nodeExtrinsic(nodePath, accounts["relayer"], relayCall, *dryRun); err != nil {
		panic(err)
	}

	fmt.Println("\nStep 10 — Verify events")
	if err := nodeRPC(nodePath, accounts["alice"], "state_getStorage('System.Events')", *dryRun); err != nil {
		panic(err)
	}
}
