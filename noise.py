import random
import numpy as np


def noise(highness, duration, start_volume, end_volume=0.0):
	sample_count = int(duration * 44100)
	samples = [0]*sample_count
	
	for i in range(sample_count):
		samples[i] = random.random() * 2 - 1
	
	samples = np.fft.fft(samples)
	
	for i in range(int(highness * sample_count), sample_count):
		samples[i] = 0.0
	
	samples = np.fft.ifft(samples)
	
	for i in range(sample_count):
		t = i / sample_count
		v = start_volume * (1-t) + end_volume * t
		samples[i] *= v
	
	samples = [s.real for s in samples]
	
	return samples