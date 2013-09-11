import requests
import os
from time import localtime, strftime

class PostRedirectValidator:

	def __init__(self):
		self.redTypeArray = ['Single Redirect', 'Index Redirect', 'Consolidation', 'Remapping']
		self.redTypeIndex = 0
		# self.indexPages = ['index.asp', 'index.php', 'index.shtml', 'index.html', 'index.jsp']
		# URL_in_pairs = [[sour URL 1, dest URL 1, (optional) error message], [sour URL 2, dest URL 2, (optional) error message]...]
		self.URL_in_pairs = []
		
		cur_dir = os.getcwd()
		filepath = cur_dir + '\\post_redirects.csv'
		if os.path.isfile(filepath):
			f = open(filepath,'r')
			for line in f:
				if "Redirection type" in line:
					splitter = line.split(':')
					redType = splitter[1].lstrip().rstrip().lower()

					print "Reading the redirect type..."
					for redTypeVar in self.redTypeArray:
						if redTypeVar in redType:
							self.redTypeIndex = self.redTypeArray.index(redTypeVar)
							break					
					print redTypeVar + "\n"

				if '.edu' in line or '.com' in line or '.org' in line:
					# print line
					splitter = line.split(',')

					if splitter[0] != '':
						sourURL = splitter[0]
					if splitter[1] != '':
						destURL = splitter[1]
						# removing line breaker
						if destURL.endswith('\n'):
							destURL = destURL[:-1]
						self.URL_in_pairs.append([sourURL,destURL,""])
			f.close()
		else:
			print "Error locating the post redirect csv file!"

	def post_redirect_validation_main(self):
		if self.URL_in_pairs:


			print "URls are loaded..."
			print "Start processing...(please leave this process running until it finishes by itself.)"

			counter = 0
			for position in range(len(self.URL_in_pairs)):

				print "#####################################"
				print "NO." + str(counter + 1) + "- entry:"
				print "Validating..."
				self.validate_redirect(self.URL_in_pairs[position][0], self.URL_in_pairs[position][1], position)
				counter = counter + 1
				print "#####################################"
			
			self.export_results()
			return "Post implementation validation process has finished."
		else:
			return "No data"


	def validate_redirect(self, sourURL, destURL, position):
		if 'http://' not in sourURL and 'https://' not in sourURL:
			sourURL = 'http://' + sourURL

		r = requests.get(sourURL, allow_redirects = False)

		if r.status_code in [301, 302]:
			
			if r.headers['location'].rstrip() == destURL.rstrip():
				self.URL_in_pairs[position][2] = "OK"
				print "OK"
			else:
				self.URL_in_pairs[position][2] = "Redirect to a different destination"
				print "Redirect to a different destination"
		else:
				self.URL_in_pairs[position][2] = "Status code is not 301 or 302"
				print "No redirection detected"


	# Write to a comma delimited file
	def export_results(self):
		cur_dir = os.getcwd()
		cur_time = str(strftime("%d%b%Y_%H%M%S", localtime()))
		
		f = open(cur_dir + '\\post_redirect_report\\validation_result_' + cur_time + '.csv', 'w+')

		f.write("Source URL,Destination URL,Comments\n")
		for urlPairs in self.URL_in_pairs:
			f.write(urlPairs[0] + ',' + urlPairs[1] + ',' + urlPairs[2]  + '\n')

		f.close()


def main():
	test = PostRedirectValidator()
	print test.post_redirect_validation_main()

main()
