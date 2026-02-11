namespace X402.Identity;

public class AgentCredential {
    public string GetEphemeralEntropy() {
        return new AgentEntropyProvider().Generate();
    }
}
