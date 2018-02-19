# GitHub-Crawler
A Python script to collect information from GitHub using its API.

This script allows to crawl information and repositories from GitHub using the GitHub REST API (https://developer.github.com/v3/search/).

Given a query, the script downloads for each repository returned by the query its ZIP file. In addition, it also generates a CSV file containing the list of repositories queried. For each query, GitHub returns a json file which is processed by this script to get information about repositories.

The GitHub API limits the queries to get 100 elements per page and up to 1,000 elements in total. To get more than 1,000 elements, the main query should be splitted in multiple subqueries using different time windows through the constant SUBQUERIES (it is a list of subqueries).

NOTE: please, take a look at the GitHub website to be sure that you do not violate any GitHub rule.
