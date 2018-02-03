# import urllib.request

# with urllib.request.urlopen('http://discovery.nationalarchives.gov.uk/details/r/D6602096') as response :
	# print(response.read());
	
# local_filename, headers = urllib.request.urlretrieve('http://discovery.nationalarchives.gov.uk/details/r/D6602096',filename='discovery_page.html')
#html = open(local_filename)

# http://discovery.nationalarchives.gov.uk/API/sandbox/index#!/SearchRecords/SearchRecords_GetRecords

import requests;
import pprint;
import pandas as pd;
import re;
import copy;
# http://discovery.nationalarchives.gov.uk/API/search/v1/records?sps.recordSeries=ADM%20159&sps.recordSeries=ADM%20188&sps.recordSeries=ADM%20337&sps.recordSeries=ADM%20339&sps.recordSeries=ADM%20362&sps.recordSeries=ADM%20363&sps.recordCollections=Records&sps.recordCollections=DigitisedRecords&sps.catalogueLevels=Level7&sps.lastName=Lomas&sps.number=JX%20125079&sps.searchQuery=*
# http://discovery.nationalarchives.gov.uk/API/search/v1/records?sps.recordSeries=SC%208&sps.dateFrom=1360-01-01&sps.dateTo=1380-12-31&sps.catalogueLevels=Level7&sps.searchQuery=*&sps.sortByOption=REFERENCE_ASCENDING&sps.batchStartMark=*
# params={"sps.recordSeries":["ADM 159","ADM 188","ADM 337","ADM 339","ADM 362","ADM 363"],"sps.recordCollections":["Records","DigitisedRecords"],"sps.catalogueLevels":"Level7","sps.searchQuery":"Cox JX 125015"} #,"sps.lastName":"Cox","sps.number":"JX 125015"
myparams={"sps.recordSeries":["SC 8"],"sps.dateFrom":"1360-01-01","sps.dateTo":"1380-12-31","sps.catalogueLevels":"Level7","sps.searchQuery":"*","sps.sortByOption":"REFERENCE_ASCENDING","sps.batchStartMark":"*","sps.resultsPageSize":1000}
headers={"Accept": "application/json"}
url="http://discovery.nationalarchives.gov.uk/API/search/v1/records"
currentBatchMark=myparams["sps.batchStartMark"]
s=requests.Session()
r=s.get(url, headers=headers, params=myparams);
rjson=r.json()
myRecords=copy.deepcopy(rjson["records"])
#write the json response out to a file, reasonably nicely formatted using pprint = pretty print
print(myparams["sps.batchStartMark"],rjson["nextBatchMark"],str(len(rjson["records"])))
with open("response.json","w",encoding="utf-8") as responseout :
	# responseout.write(pprint.pformat(rjson))
	responseout.write(pprint.pformat(myRecords))
	# #loop over the json as a dictionary extracting the description and catalogue reference for each record returned by the search
	# for i in range(0,rjson["count"]) :
		# print(str(rjson["records"][i]["description"]),str(rjson["records"][i]["reference"]))
	# pprint.pprint(rjson)
	while myparams["sps.batchStartMark"] != rjson["nextBatchMark"] :
		currentBatchMark=myparams["sps.batchStartMark"]
		myparams["sps.batchStartMark"]=rjson["nextBatchMark"]
		r=s.get(url, headers=headers, params=myparams);
		rjson=r.json()
		myRecords.extend(rjson["records"])
		print(myparams["sps.batchStartMark"],rjson["nextBatchMark"],str(len(rjson["records"])))
		# pprint.pprint(rjson)
		# responseout.write(pprint.pformat(rjson))
		responseout.write(pprint.pformat(myRecords))
		# nextBatchMark=rjson["nextBatchMark"]

df=pd.DataFrame(data=myRecords,columns=["reference","coveringDates","startDate","endDate","numStartDate","numEndDate","description","id","places"]);
#df.to_csv("myRecords.csv",index=False,encoding="cp1252");
df.to_csv("myRecords.csv",index=False,encoding="utf-8");