"""
Part of assignment for the Udemy Taming Big Data with Mapreduce and Hadoop.
Data Source: MovieLens 100k Dataset: https://grouplens.org/datasets/movielens/
"""
from mrjob.job import MRJob
from mrjob.step import MRStep


class AvgMovieRatings(MRJob):
	def configure_args(self):
		super(AvgMovieRatings, self).configure_args()
		self.add_file_option('--items', help='Path to u.item')


	def mapper(self, _, line):
		(userId, movieID, rating, timestamp) = line.split('\t')
		yield movieID, (int(rating), 1)

	def reducer_init(self):
		self.movieNames = {}
		with open("u.ITEM", encoding='ascii', errors='ignore') as f:
			for line in f:
				fields = line.split('|')
				self.movieNames[fields[0]] = fields[1]


	def _reducer_combiner(self, movieId, ratings):
		avg, count = 0, 0
		for tmp, c in ratings:
			avg = (avg*count+tmp*c)/(count + c)
			count+=c
		return (self.movieNames[movieId], (avg, count))

	def reducer(self, movieId, ratings):
		movieId, (avg, count) = self._reducer_combiner(movieId, ratings)
		yield (movieId, avg)

	def get_formatted_avgs_mapper(self, movieId, avg):
		yield '%04.2f'%float(avg), movieId

	def reducer_output_sorted(self,avg,movieIDs):
		for movieID in movieIDs:
			yield avg, movieID

	def steps(self):
		return [MRStep(reducer_init=self.reducer_init,
					mapper=self.mapper,
					reducer=self.reducer),
			MRStep(reducer_init=self.reducer_init,
					mapper=self.get_formatted_avgs_mapper,
					reducer=self.reducer_output_sorted)
		]





if __name__ == '__main__':
	AvgMovieRatings.run()