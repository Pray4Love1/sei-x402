using System;
using System.Security.Cryptography;
using System.Text;

namespace X402.Identity;

public class AgentEntropyProvider {
    public string Generate() {
        var seed = $"{Environment.MachineName}:{DateTime.UtcNow.Ticks}:x402-agent";
        var digest = SHA256.HashData(Encoding.UTF8.GetBytes(seed));
        return Convert.ToBase64String(digest).Substring(0, 32);
    }
}
