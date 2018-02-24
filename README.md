# DiscoveryAPI
Python script(s) for accessing The National Archives' Discovery API for obtaining and processing catalogue data programmatically.  Use the [API Sandbox](http://discovery.nationalarchives.gov.uk/API/sandbox/index) for initial exploration of API functionality, and creating example API calls with parameters, the script(s) here then each demonstrate the use of one end point (the script name should make it clear which).

The [API help pages](http://discovery.nationalarchives.gov.uk/API/Help) also give more information on using the API and the form taken by the output.

See Richard Dunley's blog posts on using the catalogue as data: [Catalogue as Data: the basics](http://blog.nationalarchives.gov.uk/blog/catalogue-data-basics/) and [Catalogue as Data: the Prize Papers from the 2nd Anglo-Dutch War](http://blog.nationalarchives.gov.uk/blog/catalogue-data-prize-papers-2nd-anglo-dutch-war/) and Sonia Ranade's about [Modelling our digital data](http://blog.nationalarchives.gov.uk/blog/modelling-digital-archival-data/) to understand the inspiration for the creation of these scripts.  I felt it would help people ask for new things if they had a bit more understanding as to what was already possible.

# Using the script
## Input CSV
On launching the script (or EXE) it will ask for an input CSV file.  Enter the full path to your input file or you can drag and drop from a file explorer window to the command line (at least in Windows), you'll still need to hit enter afterwards so that the script continues. Otherwise just hit enter, and the scirpt will look for an input CSV file called [discovery_api_SearchRecords_input_params.csv](https://github.com/DavidUnderdown/DiscoveryAPI/blob/master/discovery_api_SearchRecords_input_params.csv) in the current working directory (ie in most situations, in the same directory as the script itself).  The version of the file in this repository contains the parameters necessary to obtain the basic data used in Richard's first blog post (1795 records from record series SC 8, restricted to petitions from 1360-1380).
###Input parameters
Within the input CSV file you can include up to 38 columns.  The first 34 (parameter names prefixed with "sps.") are used as the URL parameters for the API call.  The remaining 4: labels, output_filepath, output_encoding, discovery_columns are for giving the list of labels expected in a structured description, the filepath(s) for the output, the text encoding to use (defaults to UTF-8) and the data fields from Discovery which to be included in the output.  To help understand what valid input looks like a CSV Schema file has also been created, [discovery_api_SearchRecords_input_params.csvs](https://github.com/DavidUnderdown/DiscoveryAPI/blob/master/discovery_api_SearchRecords_input_params.csvs) using the [CSV Schema Language 1.1](http://digital-preservation.github.io/csv-schema/csv-schema-1.1.html) created by The National Archives.  This can be used to check the structure of your own input CSV files using the [CSV Validator](http://digital-preservation.github.io/csv-validator/).

The only mandatory parameters are sps.searchQuery for the URL parameters, and output_filepath.  You can include multiple rows to send different queries to the API in one running of the script.  Note though that you can query across multiple series in one query by supplying a list of series within a single row.  ie in the sps.recordSeries field of the CSV file you can specify things like "ADM 188, ADM 362, ADM 363" (which would query across several series containing the service records of naval ratings).  It probably only really makes sense (in terms of the output you'll get) to provide a list of series which have a (near) identical set of labels.

#### Labels
A comma separated list of the labels expected to be found (ie text followed by a colon) within the Description field in Discovery.  As the input file is a CSV, the list must be enclosed in double quotes ".  A standard regex is created from this to extract the text related to each label to its own column in the ouput file.

#### output_filepath
A valid path to a file for the output.  To make the script more interoperable, some sanitisation is done on the path to ensure that it would be a valid path in Windows (though if folders within the path already exist they will not be changed).  Any folders missing from the path will be created.  If the extensions .xls or .xlsx are used then the output will be in the form of Excel files, any other (or no extension) will result in a simple CSV file (with comma as field separator).

You can also use the keyword APPEND: this will add the output to the last named file, simply appending the text at the end of the file in the case of a CSV (with a new header row), or into a new sheet in the case of Excel output.  Similar behaviour occurs if a filepath is used more than once within the input CSV file (ie in more than one row).

#### output_encoding
The text encoding to use for the output.  If left blank it will default to UTF-8.  Any valid [Python text encoding string](https://docs.python.org/3/library/codecs.html#standard-encodings) can be used.  You can also use the keyword LOCALE which will use [locale.getpreferredencoding()](https://docs.python.org/3/library/locale.html#locale.getpreferredencoding) to obtain your system's preferred encoding (this can be useful on Windows where Excel will always open a CSV file assuming it's in the system encoding).

#### discovery_columns
The fields from the Discovery API to include in the output.  If none are given the default of "reference,coveringDates,startDate,endDate,numStartDate,numEndDate,description,id,places" will be assumed.

##Output
Output will be written to the output file(s) defined in the input CSV.  The full JSON response to the API calls is now not called unless the debug flag in the script is set, in this case outptu would still go to to a file called response.json in the current working directory.

The sample input CSV file still outputs to myRecords.csv.  If you specify a filename ending .xls or .xlsx an appropriate Excel file will be created (the text encoding is still applied).

You can now also specify the text encoding for the output CSV in the input CSV.  Simple choices are utf-8, cp1252 etc for Windows encodings (anyother valid Python encoding), or LOCALE, which will cause the preferred encoding set on your computer to be used.  This can be useful if you are intending to open the CSV file in Excel.

# Building
The EXE supplied with version 2.0 was built with PyInstaller 3.3.1 on Windows 10, it can be run without an installed version of Python being present.  It should run on other 64 bit Windows versions.  It will be quite slow to start as it has to create a virtual Python environment for running the script.  PyInstaller does not provide the ability to cross-build on different platforms, so at present I'm not able to provide any other executables.

Windows 10 and the latest Pandas (22), have some quirks with PyInstaller.

## Windows 10 issue
For Windows 10 you must [install Univeral CRT (C runtime)](http://pyinstaller.readthedocs.io/en/stable/usage.html#windows) and add 'C:\\Program Files (x86)\\Windows Kits\\10\\Redist\\ucrt\\DLLs\\x64' to the pathex of the spec file (as shown in the [spec file, discovery_api_SearchRecords_amended.spec, included in the repository](https://github.com/DavidUnderdown/DiscoveryAPI/blob/master/discovery_api_SearchRecords_amended.spec)).

## Pandas issue
For Pandas there are now some hidden imports, I took the option of including a hook-pandas.py file under the PyInstaller install as described [in the answer to this Stackoverflow question](https://stackoverflow.com/questions/47318119/no-module-named-pandas-libs-tslibs-timedeltas-in-pyinstaller), using [this GitHub example of hook-pandas.py](https://github.com/lneuhaus/pyinstaller/blob/017b247064f9bd51a620cfb2172c05d63fc75133/PyInstaller/hooks/hook-pandas.py).  Hopefully this will automatically be included in later versions of PyInstaller.

## Antivirus issue
Finally, antivirus was interfering with the build, triggering the error message "UpdateResources    win32api.EndUpdateResource(hdst, 0)pywintypes.error: (5, 'EndUpdateResource', 'Access is denied.')", so I had to temporarily disable antivirus while the EXE was being built.  It may also help to run the build with Adminstrator rights.

## Supplied Windows batch file for building.
The [batch file, discovery_api_SearchRecords_build.bat, in the repository](https://github.com/DavidUnderdown/DiscoveryAPI/blob/master/discovery_api_SearchRecords_build.bat) should allow the build to be replicated (provided the hook-pandas.py file has been added).