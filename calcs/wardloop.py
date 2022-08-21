import stats

def analyze(account, character):
	char_stats = stats.fetch_stats(account, character)
	print(char_stats)

if __name__ == '__main__':
	analyze('raylu', 'rayluloop')
