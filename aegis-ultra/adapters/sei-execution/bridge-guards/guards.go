package bridgeguards

func AllowTransfer(amount int64) bool {
	return amount > 0
}
