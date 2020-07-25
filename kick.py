from wave_instrument import wave_sin

def kick(high_freq = 260, low_freq = 30, duration = 0.07, volume = 0.3, decay_factor = 0.1, wave = wave_sin):
	sample_count = int(duration * 44100)

	samples = [0]*sample_count

	x = 0
	for i in range(sample_count):
		t = i / sample_count
		
		freq = high_freq**(1-t) * low_freq**t

		x += freq / 44100
		x %= 1
		
		v = volume
		if t > 1-decay_factor:
			v *= 1 - (t - (1-decay_factor)) / decay_factor

		samples[i] = v * wave(x)
	
	return samples