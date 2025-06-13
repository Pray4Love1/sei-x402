import { base58 } from "@scure/base";
import { createKeyPairSignerFromBytes } from "@solana/kit";
import { x402Facilitator } from "@x402/core/facilitator";
import {
  PaymentPayload,
  PaymentRequirements,
  SettleResponse,
  VerifyResponse,
} from "@x402/core/types";
import { toFacilitatorEvmSigner } from "@x402/evm";
import { registerExactEvmScheme } from "@x402/evm/exact/facilitator";
import { toFacilitatorSvmSigner } from "@x402/svm";
import { registerExactSvmScheme } from "@x402/svm/exact/facilitator";
import dotenv from "dotenv";
import express from "express";
import { createWalletClient, http, publicActions } from "viem";
import { privateKeyToAccount } from "viem/accounts";
import { baseSepolia } from "viem/chains";
// Native Sei support
import {
  PaymentPayloadSchema,
  PaymentRequirementsSchema,
  settle as seiSettle,
} from "@x402/sei";
import {
  createClientSeiTestnet,
  createSignerSeiTestnet,
} from "@x402/sei/client";

dotenv.config();

/* -------------------------------------------------------------------------- */
/* Environment Setup */
/* -------------------------------------------------------------------------- */
const PORT = process.env.PORT || "4022";

if (!process.env.EVM_PRIVATE_KEY) {
  console.error("❌ EVM_PRIVATE_KEY environment variable is required");
  process.exit(1);
}
if (!process.env.SVM_PRIVATE_KEY) {
  console.error("❌ SVM_PRIVATE_KEY environment variable is required");
  process.exit(1);
}

/* -------------------------------------------------------------------------- */
/* Account Setup */
/* -------------------------------------------------------------------------- */
// EVM
const evmAccount = privateKeyToAccount(
  process.env.EVM_PRIVATE_KEY as `0x${string}`,
);
console.info("✅ EVM Facilitator:", evmAccount.address);

// SVM
const svmAccount = await createKeyPairSignerFromBytes(
  base58.decode(process.env.SVM_PRIVATE_KEY as string),
);
console.info("✅ SVM Facilitator:", svmAccount.address);

// Viem EVM client (Base Sepolia)
const viemClient = createWalletClient({
  account: evmAccount,
  chain: baseSepolia,
  transport: http(),
}).extend(publicActions);

/* -------------------------------------------------------------------------- */
/* Facilitator Setup */
/* -------------------------------------------------------------------------- */
const evmSigner = toFacilitatorEvmSigner({
  getCode: ({ address }) => viemClient.getCode({ address }),
  address: evmAccount.address,
  readContract: ({ address, abi, functionName, args }) =>
    viemClient.readContract({
      address,
      abi,
      functionName,
      args: args || [],
    }),
  verifyTypedData: (args) =>
    viemClient.verifyTypedData(args as any),
  writeContract: ({ address, abi, functionName, args }) =>
    viemClient.writeContract({
      address,
      abi,
      functionName,
      args: args || [],
    }),
  sendTransaction: ({ to, data }) =>
    viemClient.sendTransaction({ to, data }),
  waitForTransactionReceipt: ({ hash }) =>
    viemClient.waitForTransactionReceipt({ hash }),
});

const svmSigner = toFacilitatorSvmSigner(svmAccount);

const facilitator = new x402Facilitator()
  .onBeforeVerify(async (ctx) => console.log("Before verify", ctx))
  .onAfterVerify(async (ctx) => console.log("After verify", ctx))
  .onVerifyFailure(async (ctx) => console.log("Verify failure", ctx))
  .onBeforeSettle(async (ctx) => console.log("Before settle", ctx))
  .onAfterSettle(async (ctx) => console.log("After settle", ctx))
  .onSettleFailure(async (ctx) => console.log("Settle failure", ctx));

registerExactEvmScheme(facilitator, {
  signer: evmSigner,
  networks: "eip155:84532", // Base Sepolia
  deployERC4337WithEIP6492: true,
});
registerExactSvmScheme(facilitator, {
  signer: svmSigner,
  networks: "solana:EtWTRABZaYq6iMfeYKouRu166VU2xqa1", // Solana devnet
});

// Optional: Bootstrap Sei client if needed for other ops
// createClientSeiTestnet();

/* -------------------------------------------------------------------------- */
/* Express Server */
/* -------------------------------------------------------------------------- */
const app = express();
app.use(express.json());

/* -------------------------- GET /verify -------------------------- */
app.get("/verify", (_, res) => {
  res.json({
    endpoint: "/verify",
    method: "POST",
    body: {
      paymentPayload: "PaymentPayload",
      paymentRequirements: "PaymentRequirements",
    },
  });
});

/* -------------------------- POST /verify -------------------------- */
app.post("/verify", async (req, res) => {
  try {
    const { paymentPayload, paymentRequirements } = req.body as {
      paymentPayload: PaymentPayload;
      paymentRequirements: PaymentRequirements;
    };
    if (!paymentPayload || !paymentRequirements) {
      return res.status(400).json({
        error: "Missing paymentPayload or paymentRequirements",
      });
    }
    const response: VerifyResponse = await facilitator.verify(
      paymentPayload,
      paymentRequirements,
    );
    res.json(response);
  } catch (err) {
    console.error("Verify error:", err);
    res.status(500).json({
      error: err instanceof Error ? err.message : "Unknown error",
    });
  }
});

/* -------------------------- POST /settle -------------------------- */
app.post("/settle", async (req, res) => {
  try {
    const { paymentPayload, paymentRequirements } = req.body as {
      paymentPayload: PaymentPayload;
      paymentRequirements: PaymentRequirements;
    };
    if (!paymentPayload || !paymentRequirements) {
      return res.status(400).json({
        error: "Missing paymentPayload or paymentRequirements",
      });
    }

    // Native Sei handling
    if (paymentPayload.network === "sei-testnet") {
      console.log("Routing to native Sei settle");
      const signer = createSignerSeiTestnet(
        process.env.EVM_PRIVATE_KEY as `0x${string}`,
      );
      const parsedRequirements = PaymentRequirementsSchema.parse(paymentRequirements);
      const parsedPayload = PaymentPayloadSchema.parse(paymentPayload);
      const response = await seiSettle(
        signer,
        parsedPayload,
        parsedRequirements,
      );
      return res.json(response);
    }

    // Default: facilitator-based settlement (EVM / SVM)
    const response: SettleResponse = await facilitator.settle(
      paymentPayload,
      paymentRequirements,
    );
    res.json(response);
  } catch (err) {
    console.error("Settle error:", err);
    if (err instanceof Error && err.message.includes("Settlement aborted:")) {
      return res.json({
        success: false,
        errorReason: err.message.replace("Settlement aborted: ", ""),
        network: req.body?.paymentPayload?.network || "unknown",
      } as SettleResponse);
    }
    res.status(500).json({
      error: err instanceof Error ? err.message : "Unknown error",
    });
  }
});

/* -------------------------- GET /supported -------------------------- */
app.get("/supported", async (_, res) => {
  const base = facilitator.getSupported();
  res.json({
    ...base,
    kinds: [
      ...(base.kinds || []),
      {
        x402Version: 1,
        scheme: "exact",
        network: "sei-testnet",
      },
    ],
  });
});

/* -------------------------- Start Server -------------------------- */
app.listen(parseInt(PORT), () => {
  console.log(`🚀 Facilitator listening on port ${PORT}`);
});
