package metrics

import "sync/atomic"

var preventedLoss uint64

func IncrementPreventedLoss() {
	atomic.AddUint64(&preventedLoss, 1)
}

func PreventedLoss() uint64 {
	return atomic.LoadUint64(&preventedLoss)
}
