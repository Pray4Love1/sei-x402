using System;

namespace X402.Identity;

public static class AgentAuthFunction {
    public static string Run() {
        var entropy = new AgentCredential().GetEphemeralEntropy();
        return $"x402 agent entropy issued: {entropy}";
    }
}
