# This script allows to crawl information and repositories from
# GitHub using the GitHub REST API (https://developer.github.com/v3/search/).
#
# Given a query, the script downloads for each repository returned by the query its ZIP file.
# In addition, it also generates a CSV file containing the list of repositories queried.
# For each query, GitHub returns a json file which is processed by this script to get information
# about repositories.
#
# The GitHub API limits the queries to get 100 elements per page and up to 1,000 elements in total.
# To get more than 1,000 elements, the main query should be splitted in multiple subqueries
# using different time windows through the constant SUBQUERIES (it is a list of subqueries).
#
# Reference from: https://docs.github.com/en/rest/guides/getting-started-with-the-rest-api
# Authentication
# Unauthenticated clients can make 60 requests per hour.
# To get more requests per hour, we'll need to authenticate.
# In fact, doing anything interesting with the GitHub API requires authentication.
# CURRENT_TOKEN = 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

#############
# Libraries #
#############
import json
import traceback

import wget
import time
import csv
import requests
import math

#############
# Constants #
#############

URL = "https://api.github.com/search/repositories?q="  # The basic URL to use the GitHub API
# The personalized query (for instance, to get repositories from user 'rsain')
QUERY = "topic:machine-learning"
# Different sub-queries if you need to collect more than 1000 elements
SUB_QUERIES = ["+created%3A2021-06-01"]  # can put a range like `created%3A2021-04-01..2021-04-30`
PARAMETERS = "&per_page=100"  # Additional parameters for the query (by default 100 items per page)
DELAY_BETWEEN_QUERIES = 10  # The time to wait between different queries to GitHub (to avoid be banned)
OUTPUT_FOLDER = "/Users/chaiyong/Docs/Teaching/2021/GitHub-Crawler/downloads/"  # Folder where ZIP files will be stored
OUTPUT_CSV_FILE = "/Users/chaiyong/Docs/Teaching/2021/GitHub-Crawler/repositories.csv"  # Path to the CSV file generated as output
USERNAME = 'cragkhit'
TOKEN = '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'

#############
# Functions #
#############


def get_url(url, username, token):
    """ Given a URL it returns its body """
    response = requests.get(url, auth=(username, token))
    return response.json()

########
# MAIN #
########


# To save the number of repositories processed
count_of_repos = 0

# Output CSV file which will contain information about repositories
csv_file = open(OUTPUT_CSV_FILE, 'w')
repositories = csv.writer(csv_file, delimiter=',')

# Run queries to get information in json format and download ZIP file for each repository
for subquery in range(1, len(SUB_QUERIES) + 1):
    print("Processing subquery " + str(subquery) + " of " + str(len(SUB_QUERIES)) + " ...")
    # Obtain the number of pages for the current subquery (by default each page contains 100 items)
    url = URL + QUERY + str(SUB_QUERIES[subquery - 1]) + PARAMETERS
    print(url)
    data = json.loads(json.dumps(get_url(url, USERNAME, TOKEN)))
    numberOfPages = int(math.ceil(data['total_count'] / 100.0))
    print("Total = " + str(data['total_count']))
    print("No. of pages = " + str(numberOfPages))

    # Results are in different pages
    for currentPage in range(1, numberOfPages + 1):
        print("Processing page " + str(currentPage) + " of " + str(numberOfPages) + " ...")
        url = URL + QUERY + str(SUB_QUERIES[subquery - 1]) + PARAMETERS + "&page=" + str(currentPage)
        print(url)

        data = json.loads(json.dumps(get_url(url, USERNAME, TOKEN)))
        # Iteration over all the repositories in the current json content page
        try:
            for item in data['items']:
                # Obtain user and repository names
                user = item['owner']['login']
                repository = item['name']
                clone_url = item['clone_url']
                repositories.writerow([user, repository, clone_url])

        #         # # Download the zip file of the current project
        #         # print("Downloading repository '%s' from user '%s' ..." % (repository, user))
        #         # url = item['clone_url']
        #         # fileToDownload = url[0:len(url) - 4] + "/archive/master.zip"
        #         # fileName = item['full_name'].replace("/", "#") + ".zip"
        #         # wget.download(fileToDownload, out=OUTPUT_FOLDER + fileName)
        #
                # Update repositories counter
                count_of_repos = count_of_repos + 1
        except:
            print("Error: " + user + ", " + repository + "," + clone_url)
            # printing stack trace
            traceback.print_exc()
    # A delay between different sub-queries
    if subquery < len(SUB_QUERIES):
        print("Sleeping " + str(DELAY_BETWEEN_QUERIES) + " seconds before the new query ...")
        time.sleep(DELAY_BETWEEN_QUERIES)

print("DONE! " + str(count_of_repos) + " repositories have been processed.")
csv_file.close()
