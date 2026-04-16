[Setup]
AppName=Tally Connector
AppVersion=1.0
DefaultDirName={pf}\TallyConnector
DefaultGroupName=Tally Connector
OutputDir=output
OutputBaseFilename=TallyConnectorSetup
Compression=lzma
SolidCompression=yes
SetupIconFile=icon.ico

[Files]
Source: "C:\Users\acer\Desktop\hrms_tally_connector\dist\main.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\acer\Desktop\hrms_tally_connector\icon.ico"; DestDir: "{app}"

[Icons]
Name: "{group}\Tally Connector"; Filename: "{app}\main.exe"; IconFilename: "{app}\icon.ico"
Name: "{commondesktop}\Tally Connector"; Filename: "{app}\main.exe"; IconFilename: "{app}\icon.ico"

[Run]
Filename: "{app}\main.exe"; Description: "Launch Tally Connector"; Flags: nowait postinstall skipifsilent