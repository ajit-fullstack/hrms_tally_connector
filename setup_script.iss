[Setup]
AppName=Tally Connector
AppVersion=1.0
DefaultDirName={pf}\TallyConnector
DefaultGroupName=Tally Connector
OutputDir=output
OutputBaseFilename=TallyConnectorSetup
Compression=lzma
SolidCompression=yes

[Files]
Source: "C:\Users\acer\Desktop\hrms_tally_connector\dist\main.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Tally Connector"; Filename: "{app}\main.exe"
Name: "{commondesktop}\Tally Connector"; Filename: "{app}\main.exe"

[Run]
Filename: "{app}\main.exe"; Description: "Launch Tally Connector"; Flags: nowait postinstall skipifsilent