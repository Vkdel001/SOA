Sub CreateMerchantSummary()
    Dim wbSource As Workbook
    Dim wbSummary As Workbook
    Dim wsSource As Worksheet
    Dim wsSummary As Worksheet
    Dim lastRow As Long
    Dim i As Long
    Dim dict As Object
    Dim key As String
    Dim summaryRow As Long
    
    ' Turn off screen updating for better performance
    Application.ScreenUpdating = False
    Application.DisplayAlerts = False
    
    On Error GoTo ErrorHandler
    
    ' Open source file
    Set wbSource = Workbooks.Open(ThisWorkbook.Path & "\Merchant_Transaction-Merchant.xlsx")
    Set wsSource = wbSource.Sheets(1)
    
    ' Create dictionary to store grouped data
    Set dict = CreateObject("Scripting.Dictionary")
    
    ' Find last row with data
    lastRow = wsSource.Cells(wsSource.Rows.Count, "A").End(xlUp).Row
    
    ' Loop through data starting from row 2 (assuming row 1 is header)
    For i = 2 To lastRow
        ' Create unique key: TradeName|Merchant|MerchantBankAccountNo
        key = wsSource.Cells(i, 3).Value & "|" & _
              wsSource.Cells(i, 4).Value & "|" & _
              wsSource.Cells(i, 20).Value
        
        ' If key doesn't exist, initialize array
        If Not dict.Exists(key) Then
            dict(key) = Array(0, 0, 0, 0) ' TransactionAmount, TransactionCharges, TransactionTax, SettledAmount
        End If
        
        ' Add values to existing totals
        Dim tempArray As Variant
        tempArray = dict(key)
        tempArray(0) = tempArray(0) + wsSource.Cells(i, 7).Value  ' TransactionAmount
        tempArray(1) = tempArray(1) + wsSource.Cells(i, 13).Value ' TransactionCharges
        tempArray(2) = tempArray(2) + wsSource.Cells(i, 14).Value ' TransactionTax
        tempArray(3) = tempArray(3) + wsSource.Cells(i, 15).Value ' SettledAmount
        dict(key) = tempArray
    Next i
    
    ' Create new summary workbook
    Set wbSummary = Workbooks.Add
    Set wsSummary = wbSummary.Sheets(1)
    
    ' Create headers
    wsSummary.Cells(1, 1).Value = "TradeName"
    wsSummary.Cells(1, 2).Value = "Merchant"
    wsSummary.Cells(1, 3).Value = "MerchantBankAccountNo"
    wsSummary.Cells(1, 4).Value = "Total TransactionAmount"
    wsSummary.Cells(1, 5).Value = "Total TransactionCharges"
    wsSummary.Cells(1, 6).Value = "Total TransactionTax"
    wsSummary.Cells(1, 7).Value = "Total SettledAmount"
    
    ' Format headers
    With wsSummary.Range("A1:G1")
        .Font.Bold = True
        .Interior.Color = RGB(200, 200, 200)
    End With
    
    ' Write summary data
    summaryRow = 2
    Dim keyItem As Variant
    For Each keyItem In dict.Keys
        Dim keyParts As Variant
        keyParts = Split(keyItem, "|")
        
        wsSummary.Cells(summaryRow, 1).Value = keyParts(0) ' TradeName
        wsSummary.Cells(summaryRow, 2).Value = keyParts(1) ' Merchant
        wsSummary.Cells(summaryRow, 3).Value = keyParts(2) ' MerchantBankAccountNo
        wsSummary.Cells(summaryRow, 4).Value = dict(keyItem)(0) ' Total TransactionAmount
        wsSummary.Cells(summaryRow, 5).Value = dict(keyItem)(1) ' Total TransactionCharges
        wsSummary.Cells(summaryRow, 6).Value = dict(keyItem)(2) ' Total TransactionTax
        wsSummary.Cells(summaryRow, 7).Value = dict(keyItem)(3) ' Total SettledAmount
        
        summaryRow = summaryRow + 1
    Next keyItem
    
    ' Auto-fit columns
    wsSummary.Columns("A:G").AutoFit
    
    ' Format number columns
    wsSummary.Range("D2:G" & summaryRow - 1).NumberFormat = "#,##0.00"
    
    ' Save summary file
    wbSummary.SaveAs ThisWorkbook.Path & "\summary.xlsx", FileFormat:=51
    
    ' Close workbooks
    wbSource.Close SaveChanges:=False
    wbSummary.Close SaveChanges:=False
    
    ' Restore settings
    Application.DisplayAlerts = True
    Application.ScreenUpdating = True
    
    MsgBox "Summary file created successfully!" & vbCrLf & _
           "File saved as: summary.xlsx" & vbCrLf & _
           "Total unique merchants: " & dict.Count, vbInformation
    
    Exit Sub
    
ErrorHandler:
    Application.DisplayAlerts = True
    Application.ScreenUpdating = True
    MsgBox "Error: " & Err.Description, vbCritical
End Sub
