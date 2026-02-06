package latencysafeguards

import "time"

func WithinLatency(start time.Time, max time.Duration) bool {
	return time.Since(start) <= max
}
