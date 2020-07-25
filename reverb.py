from noise import noise
import numpy as np

def reverb(samples):
	n = noise(0.8, 0.6, 0.01, 0.0)
	
	n[0] = 1
	
	return list(np.convolve(samples, n))
