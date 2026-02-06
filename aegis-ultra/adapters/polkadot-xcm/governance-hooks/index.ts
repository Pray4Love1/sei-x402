export type GovernanceProposal = {
  id: string;
  feeBps: number;
};

export function approveProposal(proposal: GovernanceProposal): boolean {
  return proposal.feeBps >= 0;
}
