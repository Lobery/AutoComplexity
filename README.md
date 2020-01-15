# AutoComplexity
1.Install SourceMonitor from https://wiki.ith.intel.com/display/MediaWiki/Auto+parser+for+quality+metrics+beyond+pass+rate
2.Modify SourceMonitor.exe location in test.bat
3.Modify driver_location and complexity_filter in Query.xml
4.Run main.py.
5.Important dump files include:1)Func_changed.txt(Include all functions modified in current version against last version); 2)method_detail.csv(Include all functions complexity information scanned by SourceMonitor); 3)output.csv(Include functions in Func_changed.txt whose complexity >= filter in Query.xml)
6.Files need to be create if using pyinstaller to generate exe: config.xml, test.bat, Query.xml