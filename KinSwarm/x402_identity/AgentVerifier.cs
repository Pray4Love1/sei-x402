namespace X402.Identity;

public static class AgentVerifier {
    public static bool Verify(string entropy) => !string.IsNullOrWhiteSpace(entropy) && entropy.Length == 32;
}
