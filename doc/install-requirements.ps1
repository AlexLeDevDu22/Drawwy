Get-Content doc/requirements.txt | ForEach-Object {
    pip install $_
}
