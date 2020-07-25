from wave_instrument import WaveInstrument, wave_sin, wave_square, wave_saw, wave_triangle
from kick import kick
from noise import noise
from samples import add_samples, normalize
import random
from reverb import reverb

# pitch classes
A = 0
As = Bb = 1
B = 2
C = 3
Cs = Db = 4
D = 5
Ds = Eb = 6
E = 7
F = 8
Fs = Gb = 9
G = 10
Gs = Ab = 11

diatonic_consonant_triads = [
	(A, C, E),
	(C, E, G),
	(D, F, A),
	(E, G, B),
	(F, A, C),
	(G, B, D)
]


def pitch_to_frequency(pitch):
	return 2.0**(pitch / 12.0) * 27.5

def rhythm_to_music(bpm, rhythm):
	chords = random.sample(diatonic_consonant_triads, 4)
	random.shuffle(chords)
	
	last_tick = 0 if len(rhythm) == 0 else rhythm[-1]
	measure_count = 1 + int(last_tick / 192)
	
	# TODO : REMOVE
	# measure_count = 16
	
	minutes_per_beat = 1 / bpm
	seconds_per_beat = 60 * minutes_per_beat
	seconds_per_measure = 4 * seconds_per_beat
	
	duration_seconds = measure_count * seconds_per_measure
	
	sample_count = int(duration_seconds * 44100)
	
	kick_channel = [0.0]*sample_count
	
	everything_else_channel = [0.0]*sample_count
	
	bass = WaveInstrument(wave_saw)
	sub_bass = WaveInstrument(wave_sin)
	arp = WaveInstrument(wave_square)

	kick_samples = kick(wave=wave_triangle)
	snare_samples = noise(0.2, 0.2, 0.3)
	hat_samples = noise(0.6, 0.05, 0.3)

	rhythm_measures = [[] for i in range(measure_count)]
	for tick in rhythm:
		measure_index = tick // 192
		if measure_index < measure_count:
			rhythm_measures[tick // 192].append(tick)

	# TODO : compute this?
	stream_notes_per_measure = 24
	stream_offsets = list(range(0, 192, 192 // stream_notes_per_measure))
	
	stream_measures = set()
	
	for measure_index in range(measure_count):
		hit_offsets = [t % 192 for t in rhythm_measures[measure_index]]
		is_stream = hit_offsets == stream_offsets
		if is_stream:
			stream_measures.add(measure_index)

	for measure_index in range(measure_count):
		bass_pitch = chords[measure_index % len(chords)][0]
		if bass_pitch <= C: bass_pitch += 12
		freq = pitch_to_frequency(bass_pitch)

		for beat_index in range(4):
			bass_start_beat = 4 * measure_index + beat_index + 0.5
			bass_start_time = seconds_per_beat * bass_start_beat
			bass_duration = 0.5 * seconds_per_beat
			
			bass.add_note(everything_else_channel, (2*freq, bass_start_time, bass_duration, 0.15))
			sub_bass.add_note(everything_else_channel, (freq, bass_start_time, bass_duration, 0.2))
			
			kick_start_beat = 4 * measure_index + beat_index
			kick_start_time = seconds_per_beat * kick_start_beat
			add_samples(kick_channel, kick_start_time, kick_samples)
			
			if beat_index % 2 == 1:
				add_samples(everything_else_channel, kick_start_time, snare_samples)
			
			is_streamy = len(rhythm_measures[measure_index]) >= stream_notes_per_measure
			
			arp_notes_per_beat = 8 if is_streamy else 2
			arp_duration =  1/arp_notes_per_beat * seconds_per_beat
			if not is_streamy: arp_duration /= 2
			for step_index in range(arp_notes_per_beat):
				arp_start_beat = 4 * measure_index + beat_index + step_index / arp_notes_per_beat
				arp_start_time = seconds_per_beat * arp_start_beat
				chord = chords[measure_index % len(chords)]
				arp_pitch = chord[(beat_index * arp_notes_per_beat + step_index) % len(chord)] + 36
				arp_freq = pitch_to_frequency(arp_pitch)
				v = 0.08
				arp.add_note(everything_else_channel, (arp_freq, arp_start_time, arp_duration, v))

			hats_per_beat = 4 if is_streamy else 2
			for step_index in range(hats_per_beat):
				hat_start_beat = 4*measure_index+beat_index + step_index / hats_per_beat
				hat_start_time = seconds_per_beat * hat_start_beat
				hat_volume = 1 if step_index == 2 else 0.5
				add_samples(everything_else_channel, hat_start_time, hat_samples, hat_volume)

	# melody I guess
	max_note_ticks = 192 // 4
	prev_pitch = None
	
	for measure_index in range(measure_count):
		rhythm_measure = rhythm_measures[measure_index]

		if measure_index in stream_measures:
			rhythm_measure = list(range(192*measure_index, 192*(measure_index+1), 192 // 4))
		
		for rhythm_index, tick in enumerate(rhythm_measure):
			if rhythm_index + 1 == len(rhythm_measure):
				tick_duration = 192 - (tick % 192)
			else:
				end_tick = rhythm_measure[rhythm_index+1]
				tick_duration = min(max_note_ticks, end_tick - tick)
			
			start_time = seconds_per_measure * tick / 192
			duration = seconds_per_measure * tick_duration / 192
			
			measure_index = tick // 192
			chord = chords[measure_index % len(chords)]
			while True:
				pitch = chord[random.randint(0, len(chord)-1)]
				if pitch != prev_pitch:
					break
			freq = pitch_to_frequency(pitch + 48)
			arp.add_note(everything_else_channel, (freq, start_time, duration, 0.08))
			prev_pitch = pitch

	print('reverb...')
	everything_else_channel = reverb(everything_else_channel)

	print('mix...')
	samples = [sum(s) for s in zip(kick_channel, everything_else_channel)]
	
	print('normalize...')
	normalize(samples)
	
	return samples