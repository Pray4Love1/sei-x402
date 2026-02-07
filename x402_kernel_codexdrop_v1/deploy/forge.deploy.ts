import { ethers } from "ethers";

export async function deployVault(identity: string, sweeper: string) {
  const provider = new ethers.JsonRpcProvider(process.env.RPC_URL);
  const signer = new ethers.Wallet(process.env.DEPLOYER_KEY ?? "", provider);

  const factory = new ethers.ContractFactory(
    [
      "constructor(address _identity, address _sweeper)",
      "function rotateSweeper(address _newSweeper) external",
    ],
    "0x00",
    signer
  );

  return factory.deploy(identity, sweeper);
}
