import { verifyExactPaymentWithFees } from "./verify_exact_payment";

export async function settleExactEvm({
  tokenContract,
  payment,
  signature,
  feeQuote,
  facilitatorAddress,
}) {
  verifyExactPaymentWithFees({
    payment,
    feeQuote,
    facilitatorAddress,
  });

  const tx = await tokenContract.transferWithAuthorization(
    payment.authorization.from,
    payment.authorization.to,
    payment.authorization.value,
    payment.authorization.validAfter,
    payment.authorization.validBefore,
    payment.authorization.nonce,
    signature,
  );

  return {
    success: true,
    transaction: tx.hash,
    network: feeQuote.network,
    payer: payment.authorization.from,
  };
}
