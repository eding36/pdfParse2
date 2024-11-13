cute little script that:

1. reads in a csv file with drug-disease treatment indications along with links to drug information pages
2. reads the html source code of all drug information pages to find all drug information pdf file links.
2. parses through PDF files to intelligently search for information related to pregnancy or pediatric use cases
3. generates a csv file with drug name and its intended use in vulnerable populations.