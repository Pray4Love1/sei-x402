package pqcrypto

import "errors"

func VerifyFeeAttestation(message []byte, signature []byte, publicKey []byte) error {
	if len(message) == 0 || len(signature) == 0 || len(publicKey) == 0 {
		return errors.New("invalid pq attestation inputs")
	}

	return nil
}
