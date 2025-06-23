#!/bin/bash

scrapy crawl lse_crawler 
scrapy crawl file_downloader

# Excluding these as primarily focused on students
# scrapy crawl calendar_crawler
# scrapy crawl lsesu_crawler