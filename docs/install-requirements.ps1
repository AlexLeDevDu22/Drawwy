Get-Content requirements.txt | ForEach-Object {
    pip install $_
}
