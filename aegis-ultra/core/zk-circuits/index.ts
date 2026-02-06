export type ZkFeeProofInput = {
  paymentPayloadHash: string;
  feeBps: number;
  facilitatorId: string;
};

export type ZkFeeProof = {
  proof: string;
  publicSignals: string[];
};

export function requestFeeProof(input: ZkFeeProofInput): ZkFeeProof {
  return {
    proof: "zk-proof-placeholder",
    publicSignals: [input.paymentPayloadHash, String(input.feeBps)],
  };
}
