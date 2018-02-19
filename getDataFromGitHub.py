# This script allows to crawl information and repositories from GitHub using the GitHub REST API (https://developer.github.com/v3/search/).
#
# Given a query, the script downloads for each repository returned by the query its ZIP file.
# In addition, it also generates a CSV file containing the list of repositories queried.
# For each query, GitHub returns a json file which is processed by this script to get information about repositories.
#
# The GitHub API limits the queries to get 100 elements per page and up to 1,000 elements in total.
# To get more than 1,000 elements, the main query should be splitted in multiple subqueries using different time windows through the constant SUBQUERIES (it is a list of subqueries).
#
# As example, constant values are set to get the repositories on GitHub of the user 'rsain'.


#############
# Libraries #
#############

import wget
import time
import simplejson
import csv
import pycurl
import math
from StringIO import StringIO


#############
# Constants #
#############

URL = "https://api.github.com/search/repositories?q=" #The basic URL to use the GitHub API
QUERY = "user:rsain" #The personalized query (for instance, to get repositories from user 'rsain')
SUBQUERIES = ["+created%3A<%3D2013-12-30","+created%3A>%3D2014-01-01"] #Different subqueries if you need to collect more than 1000 elements
PARAMETERS = "&per_page=100" #Additional parameters for the query (by default 100 items per page)
DELAY_BETWEEN_QUERYS = 10 #The time to wait between different queries to GitHub (to avoid be banned)
OUTPUT_FOLDER = "/media/ruben/mydisk/Documents/PhD/Energy/Nexus4/Dictionaries/Apps/test/zips/" #Folder where ZIP files will be stored
OUTPUT_CSV_FILE = "/media/ruben/mydisk/Documents/PhD/Energy/Nexus4/Dictionaries/Apps/test/repositories.csv" #Path to the CSV file generated as output


#############
# Functions #
#############

def getUrl (url) :
	''' Given a URL it returns its body '''
	buffer = StringIO()
	c = pycurl.Curl()
	c.setopt(c.URL, url)
	c.setopt(c.WRITEDATA, buffer)
	c.perform()
	c.close()
	body = buffer.getvalue()

	return body


########
# MAIN #
########

#To save the number of repositories processed
countOfRepositories = 0

#Output CSV file which will contain information about repositories
csvfile = open(OUTPUT_CSV_FILE, 'wb')
repositories = csv.writer(csvfile, delimiter=',')

#Run queries to get information in json format and download ZIP file for each repository
for subquery in range(1, len(SUBQUERIES)+1):
	print "Processing subquery " + str(subquery) + " of " + str(len(SUBQUERIES)) + " ..."
	
	#Obtain the number of pages for the current subquery (by default each page contains 100 items)
	url = URL + QUERY + str(SUBQUERIES[subquery-1]) + PARAMETERS			
	dataRead = simplejson.loads(getUrl(url))	
	numberOfPages = int(math.ceil(dataRead.get('total_count')/100.0))

	#Results are in different pages
	for currentPage in range(1, numberOfPages+1):
		print "Processing page " + str(currentPage) + " of " + str(numberOfPages) + " ..."
		url = URL + QUERY + str(SUBQUERIES[subquery-1]) + PARAMETERS + "&page=" + str(currentPage)					
		dataRead = simplejson.loads(getUrl(url))
		
		#Iteration over all the repositories in the current json content page
		for item in dataRead['items']:
			#Obtain user and repository names
			user = item['owner']['login']
			repository = item['name']
			repositories.writerow([user, repository])
			
			#Download the zip file of the current project				
			print ("Downloading repository '%s' from user '%s' ..." %(repository,user))
			url = item['clone_url']
			fileToDownload = url[0:len(url)-4] + "/archive/master.zip"
			fileName = item['full_name'].replace("/","#") + ".zip"
			wget.download(fileToDownload, out=OUTPUT_FOLDER + fileName)
							
			#Update repositories counter
			countOfRepositories = countOfRepositories + 1

		print "DONE for current page!"	
	print "DONE for current subquery!"

	#A delay between different subqueries
	if (subquery < len(SUBQUERIES)):
		print "Sleeping " + str(DELAY_BETWEEN_QUERYS) + " seconds before the new query ..."
		time.sleep(DELAY_BETWEEN_QUERYS)

print "DONE! " + str(countOfRepositories) + " repositories have been processed."
csvfile.close()