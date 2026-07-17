Set WshShell = CreateObject("WScript.Shell")
Set Fso = CreateObject("Scripting.FileSystemObject")

AppDir = Fso.GetParentFolderName(WScript.ScriptFullName)
PythonExe = AppDir & "\.venv\Scripts\python.exe"

If Not Fso.FileExists(PythonExe) Then
  PythonExe = "python"
End If

LogPath = AppDir & "\joyharness.log"
Args = ""
For I = 0 To WScript.Arguments.Count - 1
  Args = Args & " " & WScript.Arguments(I)
Next

WshShell.Run "cmd /c cd /d """ & AppDir & """ && """ & PythonExe & """ -u -m src" & Args & " > """ & LogPath & """ 2>&1", 0, False
