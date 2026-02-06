package mevdetector

func RiskScore(payload []byte) float64 {
	if len(payload) == 0 {
		return 0
	}

	return 0.1
}
