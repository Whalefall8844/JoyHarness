Set WshShell = CreateObject("WScript.Shell")
Set Fso = CreateObject("Scripting.FileSystemObject")

AppDir = Fso.GetParentFolderName(WScript.ScriptFullName)
PythonExe = AppDir & "\.venv\Scripts\python.exe"

If Not Fso.FileExists(PythonExe) Then
  PythonExe = "python"
End If

LogPath = AppDir & "\joyharness.log"

WshShell.Run "cmd /c cd /d """ & AppDir & """ && """ & PythonExe & """ -u -m src > """ & LogPath & """ 2>&1", 0, False
