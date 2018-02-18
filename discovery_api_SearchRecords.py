## This script wraps http GET calls to The National Archives' Discovery API to download catalogue data for a given search on the SearchRecords API endpoint.
## To understand the parameters being used, and the data structure used, try out the Sandbox.
## This script expects a response as application/json, application/xml is also available from the endpoint.
## http://discovery.nationalarchives.gov.uk/API/sandbox/index#!/SearchRecords/SearchRecords_GetRecords
## Example URLs for calls, this script implements the second call, to gather catalogue data from the record series SC 8: Special Collections: Ancient Petitions
# http://discovery.nationalarchives.gov.uk/API/search/v1/records?sps.recordSeries=ADM%20159&sps.recordSeries=ADM%20188&sps.recordSeries=ADM%20337&sps.recordSeries=ADM%20339&sps.recordSeries=ADM%20362&sps.recordSeries=ADM%20363&sps.recordCollections=Records&sps.recordCollections=DigitisedRecords&sps.catalogueLevels=Level7&sps.lastName=Lomas&sps.number=JX%20125079&sps.searchQuery=*
# http://discovery.nationalarchives.gov.uk/API/search/v1/records?sps.recordSeries=SC%208&sps.dateFrom=1360-01-01&sps.dateTo=1380-12-31&sps.catalogueLevels=Level7&sps.searchQuery=*&sps.sortByOption=REFERENCE_ASCENDING&sps.batchStartMark=*

## Python standard libraries used, using Python 3.6.4:
import copy;
import pprint;
import string;
import csv;
import pathlib;
import locale;
## Additional modules required, use pip install to get these from the PyPI - the Python Package Index (https://pypi.python.org/pypi)
import requests;      #version 2.18.4, used for connecting to the API
import pandas as pd;  #version 0.22.0, data analysis package, gives us "super spreadsheet" capabilities, everything Excel can do and more
import regex;   #version 2018.2.8, third party regex library, API same as re built-in library, but additional flags and options which are needed

## First, prepare regular expression to be used to pull required info out of record description, the bits with (?P<some_name>...) allow us to refer to bits of the description by name
## note though that to match original analysis we actually only need Addressees as places is already returned as a distinct field in the JSON.
## used in get_addressees function defined below.
## Essentially for each label in the description we wrap it and its associated text within a high level group, denoted by brackets within the regex; as a specific label is not guaranteed to appear in every
## description, after the group we put a question mark to indicate this. Within this set of brackets the regex consists of the label itself, followed by a colon and a space (I've occasionally found the space 
## has been missing, so if you get unexpected results, trying making the space optional (as on Petitioners below.  Then for the descriptive text relating to a label, we wrap it in another group
## this time using the option to name it (?P<some_name>.*?) the . matches any/all characters following, * says repeated an unknown number of times and ? tells the * not to be "greedy",
## otherwise the first matching label would grab all the rest of the text.  As we expect each bit of text to end with a full stop (period) and a space, outside the named group, but inside the
## overall group for the label we say there's a full stop followed by a space \. (here we have to escape the . with \ as we want to match literally the . character, not any character.
## Then we just put the blocks for each label following the first one in the expected order of appearance.
## So for example label Label:
##		(Label: (?P<label>.*?)\. )?

## Originally did this manually: desc_fields=re.compile("(Petitioners:( )?(?P<petitioners>.*?)\. )?(Name\(s\): (?P<names>.*?)\. )?(Addressees: (?P<addressees>.*?)\. )?(Occupation: (?P<occupation>.*?)\. )?(Nature of request: (?P<nature_of_request>.*?)\. )?(Nature of endorsement: (?P<nature_of_endorsement>.*?)\. )?(Places mentioned: (?P<places_mentioned>.*?)\. )?(People mentioned: (?P<people_mentioned>.*?)\. )?")
## Now try to build regex automatically from a list of labels:
##labels=["Petitioners","Name(s)","Addressees","Occupation","Nature of request","Nature of endorsement","Places mentioned","People mentioned"]

## Now take labels from CSV file, input at command line
inputFile=input("Enter file path or name for CSV input file (or drag and drop), hit enter for default file: ").strip('"')
## If no name given default to original fixed input
if not inputFile :
	inputFile="discovery_api_SearchRecords_input_params.csv"
paramsIn=pathlib.Path(inputFile)

## check we've got a valid path, if not raise error and exit script
try :
	paramsIn.resolve(strict=True)
except FileNotFoundError:
	print("Cannot find specified input file, script will exit with error")
	raise;

with open(paramsIn,mode="r",newline='') as csvParamsIn :
	dictParamsReader=csv.DictReader(csvParamsIn)
	
	for row in dictParamsReader :
		## if there is a "labels" column in the input CSV, and that actually has some content, break up into list by splitting on commas
		if "labels" in row and row["labels"] :
			labels=row.pop("labels").split(",")
		else :
			## otherwise just create an empty list
			labels=[]
		
		## initialise list for the individual regex groups that will be created from the label list
		descfields_list=[]

		## Go through the label list for each label in turn, construct a normalised label id, and construct the high level regex group for that label and its related text
		for label in labels :
			## construct the normalised label_id, add to list of label_ids
			label_id=label
			## remove punctuation characters
			for char in string.punctuation :
				label_id=label_id.replace(char,"")
			## replace whitespace characters with underscore
			for char in string.whitespace :
				label_id=label_id.replace(char,"_")
			## casefold, to lower case as aggressively as possible as defined in Unicode
			label_id=label_id.casefold()
			## construct the group for the label and its associated text, make sure any regex metacharacters are escaped to avoid unexpected results.
			escaped_label=regex.escape(label)
			relabelgroup=r"("+escaped_label+r":( )?"+r"(?P<"+label_id+r">.*?)(\. |$))?"
			descfields_list.append(relabelgroup)
			# print(str(labels))
		## Now build the full regex, join the elements of the list into one big string using empty string as the joining character (making each group optional):
		redescfields="".join(descfields_list)
		
		if redescfields :
			## And create the compiled regex object (from this we can get the list of label_ids by using desc_fields.groupindex.keys() ).
			desc_fields=regex.compile(redescfields, flags=regex.POSIX|regex.VERSION1)   ## revised version using regex library to get left longest match using POSIX flag under VERSION1
			## Confirm the regex to be used
			print("regex for extracting data from description:",desc_fields.pattern)
			# label_start=regex.compile(r"(?r)(?<start>:|(. )|\[|\])")
		else :
			desc_fields=None
		
		## Look for other parameters that don't form part of the API call
		if "output_filepath" in row :
			if row["output_filepath"] :
				outpath=libpath.Path(row.pop("output_filepath"))
			else :
				raise RuntimeError("No output file specified")
		
		if "output_encoding" in row :
			if row["output_encoding"] :
				output_encoding=libpath.Path(row.pop("output_encoding"))
			else :
				output_encoding="utf-8"
		
		## Now construct the API call.
		## For use via the Python requests library the parameters (following the ? in the URLs above) are expressed as a Python dictionary of key-value pairs,
		## if a parameter is used with several different values (as in the first URL), the multiple values are expressed as Python list as in the first example.
		## The parameters used are explained below.  The only mandatory parameter is sps.searchQuery - but that can be set to the wildcard *.
		## The full list of available parameters can be found via the sandbox link above.
		# myparams={"sps.recordSeries":["ADM 159","ADM 188","ADM 337","ADM 339","ADM 362","ADM 363"],"sps.recordCollections":["Records","DigitisedRecords"],"sps.catalogueLevels":"Level7","sps.searchQuery":"Cox JX 125015"} #,"sps.lastName":"Cox","sps.number":"JX 125015"
		#myparams={"sps.recordSeries":["SC 8"],"sps.dateFrom":"1360-01-01","sps.dateTo":"1380-12-31","sps.catalogueLevels":"Level7","sps.searchQuery":"*","sps.sortByOption":"REFERENCE_ASCENDING","sps.batchStartMark":"*","sps.resultsPageSize":1000}
		## "sps.recordSeries":["SC 8"] - set the record series to be searched to SC 8
		
		## Now take from input CSV file
		for key in ["sps.recordSeries","sps.references","sps.recordCollections","sps.timePeriods","sps.departments","sps.taxonomySubjects","sps.closureStatuses","sps.searchRestrictionFields"] :
			## if a key in the list is present in the input CSV and has some content, split the content to turn it into a list for the url parameter construction
			if key in row and row[key] :
				row[key] = row[key].split(",")
		
		for key in row :
			if row[key] == "" :
				row[key]=None
		
		myparams=row
		# print(str(myparams))
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

		## As we're expecting to make further requests to get the full record set, copy the response out into a clean list
		myRecords=copy.deepcopy(rjson["records"])

		## So we can see progress, print out original value for batchStartMark, the returned value for batchStartMark, and the number of records returned by this request
		print(myparams["sps.batchStartMark"],rjson["nextBatchMark"],str(len(rjson["records"])))
		
		debug = False
		## Having developed the rest of the script, don't really need the JSON written out, but may be useful for debugging, so keep code
		if debug :
			## Open a file to write the json response out into (will automatically be closed once we've processed all requests), reasonably nicely formatted using pprint = pretty print
			responseout=open("response.json","w",encoding="utf-8")
			## by default, write out just the records portion included in the returned data. Swap which of the two lines immediately below is commented to write out the whole response
			# responseout.write(pprint.pformat(rjson))
			responseout.write(pprint.pformat(myRecords))
			
			##Uncomment the following line to also show the output in the command line window
			# pprint.pprint(rjson)
			
		## Keep requesting data until we have retrieved all records, at that point the nextBatchMark is not updated, so the value used for the call will match the returned value
		while (myparams["sps.batchStartMark"] != rjson["nextBatchMark"] and myparams["sps.batchStartMark"] != "null" ):
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
			if debug :
				responseout.write(pprint.pformat(myRecords))
				
				##Uncomment the following line to also show the output in the command line window
				# pprint.pprint(rjson)
		if debug :
			responseout.close()
		## Now create our equivalent of a spreadsheet, called a DataFrame.  Select just the fields we're interested in: compared to the original analysis we're also keeping
		## the machine readable versions of the covering date "startDate","endDate","numStartDate","numEndDate" which should make date related questions easier to handle,
		## and also places is already pulled out as a separate field in the JSON data, so we might as well take it, though the regex will also pull it out of the description separately
		
		## First set up various functions that will do the work of applying the regex and splitting out labelled text.
		def search_for_match(v) :
			'''Find match for each row (to be saved in temporary column in DataFrame)'''
			match=desc_fields.search(v["description"])
			
			return match
		
		def get_labelled_data(v,label_id) :
			'''Function used to extract the data associated with a given label used in the description field'''
			# match=desc_fields.search(v["description"])
			if v["match"] :
				matchdict=v["match"].groupdict()
				labelled_data=matchdict[label_id]
				## if you're not getting expected output, try uncommenting print statements below to see which descriptions are actually matching.
				if labelled_data :
					## tidy up a bit, remove any square brackets used to fill out detail to make data more consistent for analysis
					labelled_data=labelled_data.replace("[","").replace("]","")
					# print(v["reference"],label_id,labelled_data)
				else :
					# print(v["reference"],"no labelled_data found for:",v[label_id])
					## no action to be taken, just carry on
					pass;
			## return statement sets the new column in our DataFrame to the value extracted from the description field.
			else :
				print("no match object for",v["reference"],label_id)
				labelled_data=None
			return labelled_data;

		def no_extracted_data(v) :
			'''Check for rows which don't seem to have any extracted data'''
			no_extracted_data=True
			for label_id in desc_fields.groupindex.keys() :
				if v[label_id] :
					no_extracted_data=False
			if no_extracted_data :
				print("no data extracted from description for",v["reference"],v["description"])
			return no_extracted_data

		def other_possible_labels(v) :
			desc_without_known_labels=v["description"]
			other_possible_labels=[]
			for label in labels :
				desc_without_known_labels=desc_without_known_labels.replace(label+":","")
			max_possible_other_labels=desc_without_known_labels.count(":")
			if max_possible_other_labels > 0 :
				start_pos=0
				for i in range(max_possible_other_labels) :
					colon_pos=desc_without_known_labels.find(":",start_pos)
					start_pos=colon_pos+1
					begin_label_slice=max(desc_without_known_labels.rfind(".",0,colon_pos-1),desc_without_known_labels.rfind("[",0,colon_pos-1))
					print(str(begin_label_slice),str(colon_pos-1))
					new_label_candidate=desc_without_known_labels[begin_label_slice:colon_pos].strip("".join((string.whitespace,string.punctuation,string.digits)))
					other_possible_labels.append(new_label_candidate)
			if len(other_possible_labels) > 0 :
				print("Additional possible data labels found in",v["reference"],str(other_possible_labels))
				return other_possible_labels
			else :
				return None
		
		## Now create the dataframe with the most important columns from the JSON
		df=pd.DataFrame(data=myRecords,columns=["reference","coveringDates","startDate","endDate","numStartDate","numEndDate","description","id","places"]);
		
		## Apply data extraction regex to each description in turn, save resulting "match object" to new column
		if desc_fields :
			print("Finding regex matches")
			df["match"]=df.apply(search_for_match,axis=1)
			## For each label_id, pull out the related data into a new column
			for label_id in desc_fields.groupindex.keys() :
				print("label_id:",label_id)
				df[label_id]=df.apply(get_labelled_data,axis=1,args=(label_id,))
			## Look for rows that seem to have no data extracted at all.
			df["no_extracted_data"]=df.apply(no_extracted_data,axis=1)
			
			## Match object doesn't give us anything useful to include in overall output so delete the column, keeping everything else in original dataframe.
			df.drop(labels="match", axis=1, inplace=True)
		else :
			print("no desc_fields regex object")#
			df["no_extracted_data"]=True
		## check for any other possible labels in text that we didn't include in original list of labels
		df["other_possible_labels"]=df.apply(other_possible_labels,axis=1)
		
		## If you're intending to load csv file into Excel, switch the commenting of the two following lines to get Windows encoding (change cp1252 to appropriate value based on locale)
		## Can find the current preferred locale with import locale; locale.getpreferredencoding()
		#df.to_csv("myRecords.csv",index=False,encoding="cp1252");
		df.to_csv(outpath,index=False,encoding=output_encoding);