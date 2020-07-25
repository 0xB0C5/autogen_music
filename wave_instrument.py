import math

class WaveInstrument:
	def __init__(self, wave, sample_rate = 44100):
		self._wave = wave
		self._sample_rate = sample_rate
	
	def add_note(self, samples, note):
		freq, start_time, duration, volume = note
		
		start_index = int(start_time * self._sample_rate)
		end_index = int((start_time + duration) * self._sample_rate)
		
		start_index = max(0, start_index)
		end_index = min(len(samples)-1, end_index)
		sample_count = end_index - start_index
		
		for i in range(sample_count):
			samples[start_index + i] += volume * self._wave((i / self._sample_rate * freq) % 1.0)

def wave_sin(x):
	return math.sin(2.0 * math.pi * x)

def wave_square(x):
	return 1 if x > 0.5 else -1

def wave_saw(x):
	return 2 * x - 1

def wave_triangle(x):
	t = 2 * x
	t = min(t, 2 - t)
	return 2 * t - 1

