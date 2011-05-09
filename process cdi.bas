'*********************
    'RIP DISCJUGGLER IMAGE
    '*********************
    cdiInfo = ExecuteApp("""" & AppPath$ & "tools\cdirip.exe"" """ & frmMain.txtFilename.text & """ -info")


    'reinitialize global track count
    temp = 0

    'parse the session count from cdiInfo
    tmp1 = InStr(1, cdiInfo, " session(s)")
    tmp2 = InStrRev(cdiInfo, "Found ", tmp1)
    lngSessions = Mid$(cdiInfo, tmp2 + 6, tmp1 - (tmp2 + 6))

    'warn about images with more than 2 session
    If lngSessions > 2 Then
        If MsgBox("DiscJuggler images with more than 2 sessions has not been fully tested," & vbCrLf & "but you may continue. Do you wish to continue to burn this image?", vbYesNo + vbExclamation + vbDefaultButton2, "Warning") = vbNo Then
            Exit Sub
        End If
    End If

    'initialize array
    ReDim strCDIInfo(lngSessions - 1, 0) As String

    'loop the session output in cdiInfo
    For i = 1 To lngSessions

        'parse the track count for current session from cdiInfo
        tmp1 = InStr(1, cdiInfo, "Session " & CStr(i) & " has ") + (13 + Len(CStr(i)))
        tmp2 = InStr(tmp1, cdiInfo, " ")
        lngTracks = Mid$(cdiInfo, tmp1, tmp2 - tmp1)

        'create an array, first diminsion = number of sessions, 2nd diminsion = highest _
        track count in any session
        If (lngTracks - 1) > UBound(strCDIInfo, 2) Then
            ReDim strCDIInfo(lngSessions - 1, lngTracks - 1) As String
        End If

        'loop the track output in cdiInfo
        For j = 1 To lngTracks

            'global track number
            temp = temp + 1

            'parse the track type output in cdiInfo
            tmp1 = InStr(1, cdiInfo, CStr(temp) & "  Type: ") + (8 + Len(CStr(temp)))
            tmp2 = InStr(tmp1, cdiInfo, "  Size: ")

            strTrackType = Mid$(cdiInfo, tmp1, tmp2 - tmp1)

            'make sure it's a known track type
            If strTrackType <> "Mode1/2048" And strTrackType <> "Mode2/2336" And strTrackType <> "Audio/2352" Then

                MsgBox "Unknown track type: " & strTrackType, vbCritical, "Error"
                Exit Sub

            End If

            'add current track type to array
            strCDIInfo(i - 1, j - 1) = strTrackType

        Next

    Next

    '//NOTE: cdrecord 2.01.01 a35 > cannot burn data/data images with cdda correctly

    'is there more than one track in a session?
    If UBound(strCDIInfo, 2) > 0 Then
        'yes
        'is the current image a cdda data/data image?
        If strCDIInfo(0, 0) = "Mode2/2336" And strCDIInfo(0, 1) = "Audio/2352" Then
            'yes, so warn them about data/data cdda images
            If MsgBox("CDRecord cannot burn data/data DiscJuggler images with CDDA correctly," & vbCrLf & "but you may continue. Note that if the image has little-to-no space left you" & vbCrLf & "MAY burn a coaster. Do you still want to continue?", vbYesNo + vbExclamation + vbDefaultButton2, "Warning") = vbNo Then
                Exit Sub
            End If
        End If
    End If

    If FileExists(AppPath$ & "temp") = False Then MkDir AppPath$ & "temp"
    Call ShellWait("""" & AppPath$ & "tools\cdirip.exe"" """ & frmMain.txtFilename.text & """ """ & AppPath$ & "temp"" -iso" & IIf(strCDIInfo(0, 0) <> "Audio/2352", " -cut -cutall", ""), vbNormalFocus)

    '*****************************
    'SORT RIPPED DISCJUGGLER IMAGE
    '*****************************
    If FileExists(AppPath$ & "temp\tdisc.cue") = True Then Call Kill(AppPath$ & "temp\tdisc.cue")
    If FileExists(AppPath$ & "temp\tdisc2.cue") = True Then Call Kill(AppPath$ & "temp\tdisc2.cue")

    '*****************************
    'BURN RIPPED DISCJUGGLER IMAGE
    '*****************************
    'reinitialize variable
    temp = 0

    'loop the sessions
    For i = LBound(strCDIInfo, 1) To UBound(strCDIInfo, 1)

        'clear for each session
        strSession = ""

        'loop the tracks
        For j = LBound(strCDIInfo, 2) To UBound(strCDIInfo, 2)

            'configure cdrecord command line for current track
            Select Case strCDIInfo(i, j)

                Case "Mode1/2048"
                    strSession = strSession & "-data """ & AppPath$ & "temp\s" & Format$(i + 1, "00") & "t" & Format$(temp + 1, "00") & ".iso"" "

                Case "Mode2/2336"
                    strSession = strSession & "-xa """ & AppPath$ & "temp\s" & Format$(i + 1, "00") & "t" & Format$(temp + 1, "00") & ".iso"" "

                Case "Audio/2352"
                    strSession = strSession & "-audio """ & AppPath$ & "temp\s" & Format$(i + 1, "00") & "t" & Format$(temp + 1, "00") & ".wav"" "

            End Select

            'current global track
            temp = temp + 1

        Next

        'write the current session to disc
        Call ShellWait("""" & AppPath$ & "tools\cdrecord.exe"" -dev=" & strDrvID & " gracetime=2 -v driveropts=burnfree speed=" & frmMain.cboBurnSpeed.text & " " & IIf(i = UBound(strCDIInfo, 1), "-eject ", "-multi ") & IIf(InStr(1, strSession, "-xa") > 0 Or InStr(1, strSession, "-data") > 0, "-tao ", "-dao ") & strSession, vbNormalFocus)

    Next

    '********
    'FINISHED
    '********
    If MsgBox("The DiscJuggler image was successfully written." & vbCrLf & "Do you want to delete the temporary files?", vbYesNo + vbInformation, "Information") = vbYes Then
        Call Kill(AppPath$ & "temp\*.*")
        Call RmDir(AppPath$ & "temp")
    End If

    Exit Sub