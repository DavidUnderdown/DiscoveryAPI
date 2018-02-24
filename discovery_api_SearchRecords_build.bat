rem to get the pyinstaller build to work a pandas hook file was required, see https://stackoverflow.com/questions/47318119/no-module-named-pandas-libs-tslibs-timedeltas-in-pyinstaller
rem also for Windows 10, install Univeral CRT (C runtime) as described at http://pyinstaller.readthedocs.io/en/stable/usage.html#windows
rem and add 'C:\\Program Files (x86)\\Windows Kits\\10\\Redist\\ucrt\\DLLs\\x64' to the pathex of the spec file
rem antivirus software can also interfere with the build so you may need to temporarily disable real-time scanning:
rem look out for "UpdateResources    win32api.EndUpdateResource(hdst, 0)pywintypes.error: (5, 'EndUpdateResource', 'Access is denied.')"

pyinstaller --clean --onefile discovery_api_SearchRecords_amended.spec