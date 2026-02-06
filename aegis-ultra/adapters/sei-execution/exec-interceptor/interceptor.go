package execinterceptor

import "errors"

type FeeSplit struct {
	Facilitator uint64
	Insurance   uint64
	Validator   uint64
}

func ValidateFee(fee int64) error {
	if fee < 0 {
		return errors.New("invalid fee")
	}

	return nil
}

func EnforceFacilitatorFee(amount uint64, paid uint64, requiredBps uint64) bool {
	return paid*10_000 >= amount*requiredBps
}

func SplitFee(total uint64) FeeSplit {
	return FeeSplit{
		Facilitator: total * 70 / 100,
		Insurance:   total * 20 / 100,
		Validator:   total * 10 / 100,
	}
}
