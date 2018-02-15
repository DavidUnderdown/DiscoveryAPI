# DiscoveryAPI
Python script(s) for accessing The National Archives' Discovery API for obtaining and processing catalogue data programmatically.  Use the Sandbox, http://discovery.nationalarchives.gov.uk/API/sandbox/index, for initial exploration of API functionality, and example API calls with parameters, the script(s) here then each demonstrate the use of one end point (the script name should make it clear which).

The [API help pages](http://discovery.nationalarchives.gov.uk/API/Help) also give more information on using the API and the form taken by the output.

See Richard Dunley's blog posts on using the catalogue as data: [Catalogue as Data: the basics](http://blog.nationalarchives.gov.uk/blog/catalogue-data-basics/) and [Catalogue as Data: the Prize Papers from the 2nd Anglo-Dutch War](http://blog.nationalarchives.gov.uk/blog/catalogue-data-prize-papers-2nd-anglo-dutch-war/) and Sonia Ranade's about [Modelling our digital data](http://blog.nationalarchives.gov.uk/blog/modelling-digital-archival-data/) to understand the inspiration for the creation of these scripts.  I felt it would help people ask for new things if they had a bit more understanding as to what was already possible.

The script currently requires an input CSV file called [discovery_api_SearchRecords_input_params.csv](https://github.com/DavidUnderdown/DiscoveryAPI/blob/master/discovery_api_SearchRecords_input_params.csv) to be in the working directory (ie in most situations, this file should be in the same directory as the script itself).  The version of the file in this repository contains the parameters necessary to obtain the basic data used in Richard's first blog post (1795 records from record series SC 8, restricted to pettitions from 1360-1380).

It will output the full JSON returned by API to a file called response.json (this can be quite large) and the slimmed down CSV file called myRecords.csv.  Again, both of these will simply be written to the current working directory at present.
