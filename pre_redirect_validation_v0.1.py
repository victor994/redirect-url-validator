import requests
import os
from time import localtime, strftime

class RedirectValidator:

	def __init__(self):
		self.redTypeArray = ['single redirect', 'index redirect', 'consolidation', 'remapping']
		self.redTypeIndex = 0
		self.indexPages = ['index.asp', 'index.php', 'index.shtml', 'index.html', 'index.jsp']
		self.sourURLs = []
		self.destURLs = []
		# goodPairs = [[sour URL 1, dest URL 1], [sour URL 2, dest URL 2]...]
		self.goodPairs = []
		# badPairs = [[sour URL 1, dest URL 1, error message], [sour URL 2, dest URL 2, error message]...]
		self.badPairs = []

		cur_dir = os.getcwd()
		filepath = cur_dir + '/pre_redirects.csv'
		
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
						sourURL = splitter[0].lstrip().rstrip()
						self.sourURLs.append(sourURL)
					if splitter[1] != '':
						destURL = splitter[1].lstrip().rstrip()
						# removing line breaker
						if destURL.endswith('\n'):
							destURL = destURL[:-1]
						self.destURLs.append(destURL)
			f.close()
		else:
			print "Error locating the redirect csv file!"


	def check_if_looping(self, sourURL, destURL):
		if sourURL == destURL:
			self.badPairs.append([sourURL, destURL, "Source URL and destination URL are the same"])
			return True
		else:
			return False


	def validate_sourURL(self, sourURL, destURL):
		destURL = destURL.rstrip()
		sourURL = sourURL.rstrip()
		if sourURL in (x[0] for x in self.goodPairs):
			self.badPairs.append([sourURL, destURL, "Source URL has occurred once"])
			return False
		# find if the redirect is already in place
		elif self.if_redirected(sourURL) == destURL or self.if_redirected(sourURL) == destURL + "/" or self.if_redirected(sourURL) + 'index.php' == destURL or self.if_redirected(sourURL) + 'index.shtml' == destURL:			
			self.badPairs.append([sourURL, destURL, "Redirect already exists"])
			return False
		#elif self.if_url_ok(sourURL) == False:
		#	self.badPairs.append([sourURL, destURL, sourURL + " should return 200 or 201"])
		#	return False
		else:
			return True


	def validate_destURL(self, sourURL, destURL):
		# check if destination url exists
		if self.if_url_ok(destURL):
			return "OK"
		# check if destination url is being redirect. The chain redirect should not happen.
		elif self.if_redirected(destURL) != 'No redirect':			
			return "Destination URL is currently being redirected too"
		else:			
			return "Destination URL should return 200 or 201"


	def sourceURL_format_comment(self, sourURL):
		# Leave comments on the source URL for attention
		# Single redirect: source URL should end with page extention, such as php, or shtml for current CMS implementation
		# Index redirect: source URL should end with trailing slash, such as sydney.edu.au/dir/
		# Consolidation: source URL should end with trailing slash, such as sydney.edu.au/dir/
		# Remapping: source URL should end with trailing slash, such as sydney.edu.au/dir/

		# if it's single redirect type
		if self.redTypeIndex == 0:
			if sourURL[-1:] == '/':
				return "Index page URL should end with index.php or index.shtml"
			elif sourURL[-6:] != '.shtml' and sourURL[-4:] != '.php':
				return "Ambigious source URL."
			else:
				return "OK"
		return "Unknown redirect type."


	def if_url_ok(self, url):
		if 'http://' not in url and 'https://' not in url:
			url = 'http://' + url

		r = requests.get(url, allow_redirects = False)
			
		if r.status_code in [200, 201]:
			return True
		else:
			return False

	def if_redirected(self, url):
		if 'http://' not in url and 'https://' not in url:
			url = 'http://' + url
		
		r = requests.get(url, allow_redirects = False)
		if r.status_code in [301, 302]:
			return r.headers['location']
		else:
			return "No redirect"

	# Write badPairs and goodPairs to separate files
	def export_results(self):
		cur_dir = os.getcwd()
		cur_time = str(strftime("%d%b%Y_%H%M%S", localtime()))
		if self.goodPairs:
			print "Generate the list of good URLs..."
			f = open(cur_dir + '/pre_redirect_report/redirect_' + cur_time + '_successful.csv', 'w+')

			f.write("Source URL,Destination URL,Comments\n")

			for urlPairs in self.goodPairs:
				f.write(urlPairs[0] + ',' + urlPairs[1] + ',' + (urlPairs[2] if urlPairs[2] else ' ') + '\n')

			f.close()
			print "Finished\n"

		if self.badPairs:

			print "Generate the list of bad URLs..."
			f = open(cur_dir + '/pre_redirect_report/redirect_' + cur_time + '_failed.csv', 'w+')

			f.write("Source URL,Destination URL,Comments\n")
			for urlPairs in self.badPairs:
				f.write(urlPairs[0] + ',' + urlPairs[1] + ',' + (urlPairs[2] if urlPairs[2] else ' ')  + '\n')

			f.close()
			print "Finished\n"

		f = open(cur_dir + '/pre_redirect_report/Worktask_for_hosting_' + cur_time + '.txt', 'w+')

		f.write("Redirection type: " + self.redTypeArray[self.redTypeIndex] + '\n')		

		if self.goodPairs:
			f.write("Original URL:\n")

			print "Generate a work task file for hosting team..."
			for urlPairs in self.goodPairs:
				f.write(urlPairs[0] + '\n')
			
			f.write("Destination URL:\n")
			for urlPairs in self.goodPairs:
				f.write(urlPairs[1] + '\n')

		f.close()		
		print "Finished\n"

	def validate_URLs(self):
	############################################################################################################################################
	# Input: two lists of source and destination URLs in pair
	# 1.  Check if the number of source URLs matches the destination URLs. If no, quite the program with error.
	# 2.  Read one pair of URLs each time. Check if source url is the same as destination url. If yes, append to the badPairs list; If no, continue;
	# 3.1 Check if source url already exist in goodPairs. If yes, append to the badPairs list; If no, continue;
	# 3.2 Check if source url returns 301 or 302.
	# 3.2.1 Check if temp or permanent location is the same as the destination url. If yes, append to the badPairs; If no, continue;
	# REMOVED - 3.3 Check if source url returns 200 or 201. If no, append to the badPairs list; If yes, continue; 
	# 4.  Check if destination url returns 200 or 201. If yes, append to the goodPairs list. If no, continue;
	# 4.1 Check if destination url is redirected. If yes, append to the badPairs. If no, append to the badPairs with a different code;	
	############################################################################################################################################
		if self.sourURLs and self.destURLs:
			if len(self.sourURLs) != len(self.destURLs):
				print "The process has terminated unexpectedly. \nThe number of source URLs does not match destination URLs."
				return "The process has terminated unexpectedly. \nThe number of source URLs does not match destination URLs."
			else:
				counter = 0
				print "URls are loaded..."
				print "Start processing...(please leave this process running until it finishes by itself.)"
				print "#####################################"
				print "NO." + str(counter + 1) + "- entry:\n"
				for sourURL in self.sourURLs:
					destURL = self.destURLs[counter]

					print "Checking if looping..."
					if self.check_if_looping(sourURL, destURL):
						counter = counter + 1
						print "Loop detected: Source URL is the same as the destination URL.\n Skip to the next pair of URLs.\n"
						continue;

					print "No, continue\n"

					print "Checking source URL by its own..."
					if self.validate_sourURL(sourURL, destURL):
						print "Finished\n"
						print "Check destination URL by its own"
						result = self.validate_destURL(sourURL, destURL)
						print "Finished\n"
						if result == "OK":
							print "Loading comment: "
							comment = self.sourceURL_format_comment(sourURL)
							print comment + "\n"
							# print sourURL
							print "Add to the successful list...\n"
							self.goodPairs.append([sourURL, destURL, comment])
						else:
							print "Add to the failed list...\n"
							self.badPairs.append([sourURL, destURL, result])

					print "#####################################\n"				

					counter = counter + 1
					if (counter < len(self.sourURLs)): 
						print "NO. " + str(counter + 1) + " entry:\n"	

				self.export_results()
				print "The process has finished successfully."
				return "The process has finished successfully."
		else:
			print "The process has terminated unexpectedly. \nEither Source URLs or destination URLs is NULL."
			return "The process has terminated unexpectedly. \nEither Source URLs or destination URLs is NULL."
			
def main():
	test = RedirectValidator()
	test.validate_URLs()

main()
