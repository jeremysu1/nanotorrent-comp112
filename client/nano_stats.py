# nano_stats.py
# Library of statistical functions 

def ewma(sample_avg, moving_avg):
	''' Returns the exponential weighted moving average'''

	alpha = 0.125 # conventional
	return (1 - alpha) * moving_avg + alpha * sample_avg

