; ─────────────────────────────────────────────────────────────────────
;  VaultPy — Inno Setup Installer Script
;  
;  HOW TO USE:
;  1. Download and install Inno Setup from https://jrsoftware.org/isinfo.php
;  2. Run build.bat first to generate dist\VaultPy.exe
;  3. Open this file in Inno Setup and click Build > Compile
;  4. Your installer will appear in the "installer_output" folder
; ─────────────────────────────────────────────────────────────────────

[Setup]
; App identity
AppName=VaultPy
AppVersion=1.0.0
AppPublisher=Your Name
AppPublisherURL=https://github.com/yourusername/vaultpy

; Installer behavior
DefaultDirName={autopf}\VaultPy
DefaultGroupName=VaultPy
AllowNoIcons=yes
OutputDir=installer_output
OutputBaseFilename=VaultPy_Setup
Compression=lzma2
SolidCompression=yes

; Windows version requirement
MinVersion=10.0

; Installer appearance
WizardStyle=modern
SetupIconFile=
UninstallDisplayIcon={app}\VaultPy.exe

; Privileges — install for current user only (no admin needed)
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog


[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"


[Tasks]
; Ask user if they want a desktop shortcut
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"


[Files]
; The main executable built by PyInstaller
Source: "dist\VaultPy.exe"; DestDir: "{app}"; Flags: ignoreversion


[Icons]
; Start Menu shortcut
Name: "{group}\VaultPy"; Filename: "{app}\VaultPy.exe"
Name: "{group}\Uninstall VaultPy"; Filename: "{uninstallexe}"

; Desktop shortcut (only if user chose it above)
Name: "{autodesktop}\VaultPy"; Filename: "{app}\VaultPy.exe"; Tasks: desktopicon


[Run]
; Offer to launch the app right after installation
Filename: "{app}\VaultPy.exe"; Description: "Launch VaultPy now"; Flags: nowait postinstall skipifsilent


[UninstallDelete]
; Clean up vault data folder on uninstall (optional — comment out to preserve user data)
; Type: filesandordirs; Name: "{userdocs}\.vaultpy"
