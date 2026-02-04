import {
  keccak256,
  encodeAbiParameters,
  hashMessage,
  recoverAddress,
} from "viem";
import { privateKeyToAccount } from "viem/accounts";

export type FacilitatorFeeQuote = {
  network: string;
  scheme: "exact";
  asset: {
    address: `0x${string}`;
    decimals: number;
  };
  maxGasFee: string;
  expiry: number;
  signature: `0x${string}`;
};

export async function signFacilitatorFeeQuote(
  params: Omit<FacilitatorFeeQuote, "signature">,
  privateKey: `0x${string}`,
): Promise<FacilitatorFeeQuote> {
  const digest = keccak256(
    encodeAbiParameters(
      [
        { type: "string" },
        { type: "string" },
        { type: "address" },
        { type: "uint8" },
        { type: "uint256" },
        { type: "uint256" },
      ],
      [
        params.network,
        params.scheme,
        params.asset.address,
        params.asset.decimals,
        BigInt(params.maxGasFee),
        BigInt(params.expiry),
      ],
    ),
  );

  const account = privateKeyToAccount(privateKey);
  const signature = await account.signMessage({ message: { raw: digest } });

  return { ...params, signature };
}

export function verifyFacilitatorFeeQuote(
  quote: FacilitatorFeeQuote,
  facilitatorAddress: `0x${string}`,
) {
  if (Date.now() / 1000 > quote.expiry) {
    throw new Error("Facilitator fee quote expired");
  }

  const digest = keccak256(
    encodeAbiParameters(
      [
        { type: "string" },
        { type: "string" },
        { type: "address" },
        { type: "uint8" },
        { type: "uint256" },
        { type: "uint256" },
      ],
      [
        quote.network,
        quote.scheme,
        quote.asset.address,
        quote.asset.decimals,
        BigInt(quote.maxGasFee),
        BigInt(quote.expiry),
      ],
    ),
  );

  const recovered = recoverAddress({
    hash: hashMessage({ raw: digest }),
    signature: quote.signature,
  });

  if (recovered.toLowerCase() !== facilitatorAddress.toLowerCase()) {
    throw new Error("Invalid facilitator fee quote signature");
  }
}
