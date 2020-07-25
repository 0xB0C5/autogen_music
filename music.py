import wave
import struct
from rhythm2music import rhythm_to_music

TICKS_PER_MEASURE = 192
TICKS_PER_BEAT = TICKS_PER_MEASURE // 4

def write_samples(filename, samples):
	samples = [int((s+1.0)/2.0 * (1 << 16)) - (1 << 15) for s in samples]
	samples = [max(-(1 << 15), s) for s in samples]
	samples = [min((1 << 15)-1, s) for s in samples]

	file = wave.open(filename, 'wb')

	file.setnchannels(1)
	file.setsampwidth(2)
	file.setframerate(44100)
	for sample in samples:
		file.writeframesraw(struct.pack('<h', sample))

	file.close()

chart_name = 'amazing_170'
chart_path = 'charts/' + chart_name + '.txt'
bpm = float(chart_name.split('_')[-1])

notes_str = open(chart_path, 'r').read()
measure_strs = notes_str.split(',')
measures = [s.strip().split('\n') for s in measure_strs]

rhythm = []
for measure_index, measure in enumerate(measures):
	start_tick = TICKS_PER_MEASURE * measure_index
	
	for note_index, note in enumerate(measure):
		if any(c in note for c in '124'):
			tick = start_tick + (note_index * TICKS_PER_MEASURE) // len(measure)
			rhythm.append(tick)

music = rhythm_to_music(bpm, rhythm)

write_samples('music/' + chart_name + '.wav', music)