#define AppName "SUDOMG GhostNote"
#ifndef AppVersion
  #define AppVersion "1.2.0"
#endif

[Setup]
AppId={{8B6F2F1E-7C41-4B83-9E8D-GHOSTNOTE01}
AppName={#AppName}
AppVerName={#AppName}
AppVersion={#AppVersion}
UninstallDisplayName={#AppName}
AppPublisher=SUDOMG
DefaultDirName={autopf}\SUDOMG GhostNote
DefaultGroupName=SUDOMG GhostNote
OutputDir=..\dist\installer
OutputBaseFilename=SUDOMG-GhostNote-Setup
SetupIconFile=..\assets\icons\GhostNote.ico
UninstallDisplayIcon={app}\GhostNote.exe
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
DisableProgramGroupPage=yes

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Files]
Source: "..\dist\GhostNote\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\SUDOMG GhostNote"; Filename: "{app}\GhostNote.exe"
Name: "{autodesktop}\SUDOMG GhostNote"; Filename: "{app}\GhostNote.exe"; Tasks: desktopicon

[Registry]
Root: HKA; Subkey: "Software\Classes\Directory\Background\shell\GhostNote"; ValueType: string; ValueName: ""; ValueData: "Add GhostNote"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\Directory\Background\shell\GhostNote"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\GhostNote.exe"
Root: HKA; Subkey: "Software\Classes\Directory\Background\shell\GhostNote\command"; ValueType: string; ValueName: ""; ValueData: """{app}\GhostNote.exe"" new"

[UninstallRun]
Filename: "powershell.exe"; Parameters: "-NoProfile -NonInteractive -WindowStyle Hidden -Command ""Get-ScheduledTask | Where-Object {{ $_.TaskName -eq 'GhostNote Capture Prompts' }} | Unregister-ScheduledTask -Confirm:$false"""; Flags: runhidden

[Run]
Filename: "{app}\GhostNote.exe"; Description: "Launch SUDOMG GhostNote"; Flags: nowait postinstall skipifsilent

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
var
  OldPath, NewParent, NewPath, ConfigPath: String;
  OldDbPath, NewDbPath, ConfigText: String;
  ConfigAnsi: AnsiString;
begin
  if CurStep = ssInstall then
  begin
    OldPath := ExpandConstant('{userappdata}\GhostNote');
    NewParent := ExpandConstant('{userappdata}\SUDOMG');
    NewPath := NewParent + '\GhostNote';

    if DirExists(OldPath) and not DirExists(NewPath) then
    begin
      ForceDirectories(NewParent);
      RenameFile(OldPath, NewPath);
    end;

    ConfigPath := NewPath + '\database.json';

    if FileExists(ConfigPath) then
    begin
      OldDbPath := OldPath + '\ghostnote.db';
      NewDbPath := NewPath + '\ghostnote.db';

      StringChangeEx(OldDbPath, '\', '\\', True);
      StringChangeEx(NewDbPath, '\', '\\', True);

      if LoadStringFromFile(ConfigPath, ConfigAnsi) then
      begin
        ConfigText := String(ConfigAnsi);

        if StringChangeEx(ConfigText, OldDbPath, NewDbPath, True) > 0 then
        begin
          ConfigAnsi := AnsiString(ConfigText);
          SaveStringToFile(ConfigPath, ConfigAnsi, False);
        end;
      end;
    end;
  end;
end;
