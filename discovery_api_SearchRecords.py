## This script wraps http GET calls to The National Archives' Discovery API to download catalogue data for a given search on the SearchRecords API endpoint.
## To understand the parameters being used, and the data structure used, try out the Sandbox.
## This script expects a response as application/json, application/xml is also available from the endpoint.
## http://discovery.nationalarchives.gov.uk/API/sandbox/index#!/SearchRecords/SearchRecords_GetRecords

## Python standard libraries used, using Python 3.6.4:
import copy;
import pprint;
import re;
## Additional modules required, use pip install to get these from the PyPI - the Python Package Index (https://pypi.python.org/pypi)
import requests;      #version 2.18.4, used for connecting to the API
import pandas as pd;  #version 0.22.0, data analysis package, gives us "super spreadsheet" capabilities, everything Excel can do and more
## Example URLs for calls, this script implements the second call, to gather catalogue data from the record series SC 8: Special Collections: Ancient Petitions
# http://discovery.nationalarchives.gov.uk/API/search/v1/records?sps.recordSeries=ADM%20159&sps.recordSeries=ADM%20188&sps.recordSeries=ADM%20337&sps.recordSeries=ADM%20339&sps.recordSeries=ADM%20362&sps.recordSeries=ADM%20363&sps.recordCollections=Records&sps.recordCollections=DigitisedRecords&sps.catalogueLevels=Level7&sps.lastName=Lomas&sps.number=JX%20125079&sps.searchQuery=*
# http://discovery.nationalarchives.gov.uk/API/search/v1/records?sps.recordSeries=SC%208&sps.dateFrom=1360-01-01&sps.dateTo=1380-12-31&sps.catalogueLevels=Level7&sps.searchQuery=*&sps.sortByOption=REFERENCE_ASCENDING&sps.batchStartMark=*

## prepare regular expression to be used to pull required info out of record description, the bits with (?P<some_name>...) allow us to refer to bits of the description by name
## note though that to match original analysis we actually only need Addressees as places is already returned as a distinct field in the JSON.
## used in get_addressees function defined below.
# desc_fields=re.compile("(Petitioners:( )?(?P<petitioners>.*\. ))?(Name\(s\): (?P<names>.*\. ))?(Addressees: (?P<addressees>.*\. ))?(Occupation: (?P<occupation>.*\. ))?(Nature of request: (?P<nature_of_request>.*\. ))?(Nature of endorsement: (?P<nature_of_endorsement>.*\. ))?(Places mentioned: (?P<places_mentioned>.*\. ))?(People mentioned: (?P<people_mentioned>.*\. ))?")
desc_fields=re.compile("(Petitioners:( )?(?P<petitioners>.*?)\. )?(Name\(s\): (?P<names>.*?)\. )?(Addressees: (?P<addressees>.*?)\. )?(Occupation: (?P<occupation>.*?)\. )?(Nature of request: (?P<nature_of_request>.*?)\. )?(Nature of endorsement: (?P<nature_of_endorsement>.*?)\. )?(Places mentioned: (?P<places_mentioned>.*?)\. )?(People mentioned: (?P<people_mentioned>.*?)\. )?")

def get_addressees(v) :
	'''Function used to extract the addressees of petition our of the description field'''
	match=desc_fields.search(v["description"])
	if match :
		matchdict=match.groupdict()
		addressees=matchdict["addressees"]
		## if you're not getting expected output, try uncommenting print statements below to see which descriptions are actually matching.
		if addressees :
			##tidy up a bit, remove any square brackets used to fill out detail to make data more consistent for analysis
			addressees=addressees.replace("[","").replace("]","")
			# print(v["reference"],"adressees",addressees)
		else :
			# print("no addressees found for:",v("reference"))
			## no action to be taken, just carry on
			pass;
	## return statement sets the new column in our DataFrame to the value extracted from the description field.
	return addressees;

## For use via the Python requests library the parameters (following the ? in the URLs above) are expressed as a Python dictionary of key-value pairs,
## if a parameter is used with several different values (as in the first URL), the multiple values are expressed as Python list as in the first example.
## The parameters used are explained below.  The only mandatory parameter is sps.searchQuery - but that can be set to the wildcard *.
## The full list of available parameters can be found via the sandbox link above.
# myparams={"sps.recordSeries":["ADM 159","ADM 188","ADM 337","ADM 339","ADM 362","ADM 363"],"sps.recordCollections":["Records","DigitisedRecords"],"sps.catalogueLevels":"Level7","sps.searchQuery":"Cox JX 125015"} #,"sps.lastName":"Cox","sps.number":"JX 125015"
myparams={"sps.recordSeries":["SC 8"],"sps.dateFrom":"1360-01-01","sps.dateTo":"1380-12-31","sps.catalogueLevels":"Level7","sps.searchQuery":"*","sps.sortByOption":"REFERENCE_ASCENDING","sps.batchStartMark":"*","sps.resultsPageSize":1000}
## "sps.recordSeries":["SC 8"] - set the record series to be searched to SC 8
## "sps.dateFrom":"1360-01-01","sps.dateTo":"1380-12-31" - set the date range we're interested (based on the Covering Dates of the record)
## "sps.catalogueLevels":"Level7" - define what type of records we're interested in Level7 indicates items, in the main TNA catalogue that is the lowest level, 1 = lettercode, 2 = division, 3 = series, 4 = subseries, 5 = subsubseries, 6 = piece
## "sps.searchQuery":"*" - we're searching with a wildcard as we just want everything in the series within the given date range, this could be set to an explicit string for more specific searches
## "sps.sortByOption":"REFERENCE_ASCENDING" - results will be sorted in reference order from lowest to highest.  This will only be done if fewer than 10000 records are returned
## "sps.batchStartMark":"*" - enables deep paging of results, requery updating this with the value included in the returned data to get the next page of result.
## "sps.resultsPageSize":1000 - number of records to be returned in each page of results, 1000 is the maximum.

## The only header required is that to indicate we want data returned as json
headers={"Accept": "application/json"}

## Set the base URL for the API endpoint
url="http://discovery.nationalarchives.gov.uk/API/search/v1/records"

## As we'll have to page through the data returned by the endpoint, based on batchStartMark, we run the series of queries within a session
s=requests.Session()

## make the first GET request, put the response into variable r.  See http://docs.python-requests.org/en/master/user/quickstart/ for info
r=s.get(url, headers=headers, params=myparams);

## check we have an OK response from the server (ie not a 404 not found etc), an exception will be raised, terminating script execution if not
r.raise_for_status()

## use the built-in JSON interpreter to give us Python data structures (lists/dicts) representation the JSON returned from the server
rjson=r.json()

## print total (expected) record count from response
print("Total records to be retrieved:",rjson["count"])

## as we're expecting to make further requests to get the full record set, copy the response out into a clean list
myRecords=copy.deepcopy(rjson["records"])

## so we can see progress, print out original value for batchStartMark, the returned value for batchStartMark, and the number of records returned by this request
print(myparams["sps.batchStartMark"],rjson["nextBatchMark"],str(len(rjson["records"])))
## open a file to write the json response out into (will automatically be closed once we've processed all requests), reasonably nicely formatted using pprint = pretty print
with open("response.json","w",encoding="utf-8") as responseout :
	## by default, write out just the records portion included in the returned data. Swap which of the two lines immediately below is commented to write out the whole response
	# responseout.write(pprint.pformat(rjson))
	responseout.write(pprint.pformat(myRecords))
	
	##Uncomment the following line to also show the output in the command line window
	# pprint.pprint(rjson)
	
	## Keep requesting data until we have retrieved all records, at that point the nextBatchMark is not updated, so the value used for the call will match the returned value
	while myparams["sps.batchStartMark"] != rjson["nextBatchMark"] :
		## Update the parameter set with the returned value for nextBatchMark so we can get the next portion of data with our next request
		myparams["sps.batchStartMark"]=rjson["nextBatchMark"]
		
		## Make our next GET request
		r=s.get(url, headers=headers, params=myparams);
		
		## Again, decode the JSON returned
		rjson=r.json()
		
		## Add the whole new set of records that have been returned to our master list
		myRecords.extend(rjson["records"])
		
		## so we can see progress, print out original value for batchStartMark, the returned value for batchStartMark, and the number of records returned by this request
		print(myparams["sps.batchStartMark"],rjson["nextBatchMark"],str(len(rjson["records"])))
		
		## by default, write out just the records portion included in the returned data. Swap which of the two lines immediately below is commented to write out the whole response
		# responseout.write(pprint.pformat(rjson))
		responseout.write(pprint.pformat(myRecords))
		
		##Uncomment the following line to also show the output in the command line window
		# pprint.pprint(rjson)

## Now create our equivalent of a spreadsheet, called a DataFrame.  Select just the fields we're interested in: compared to the original analysis we're also keeping
## the machine readable versions of the covering date "startDate","endDate","numStartDate","numEndDate" which should make date related questions easier to handle,
## and also places is already pulled out as a separate field in the JSON data, so we might as well take it, rather than needing to pull it out of the description separately
df=pd.DataFrame(data=myRecords,columns=["reference","coveringDates","startDate","endDate","numStartDate","numEndDate","description","id","places"]);

df["addressees"]=df.apply(get_addressees,axis=1)

## If you're intending to load csv file into Excel, switch the commenting of the two following lines to get Windows encoding (change cp1252 to appropriate value based on locale)
#df.to_csv("myRecords.csv",index=False,encoding="cp1252");
df.to_csv("myRecords.csv",index=False,encoding="utf-8");