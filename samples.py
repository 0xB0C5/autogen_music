def add_samples(dest_samples, start_time, src_samples, volume = 1):
	start_index = int(44100 * start_time)
	end_index = min(len(dest_samples), start_index + len(src_samples))
	sample_count = end_index - start_index
	for i in range(sample_count):
		dest_samples[start_index + i] += volume * src_samples[i]


def normalize(samples):
	high = max(samples)
	low = min(samples)
	for i in range(len(samples)):
		samples[i] = (samples[i] - low) / (high - low) * 2 - 1