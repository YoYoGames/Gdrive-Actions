# Gdrive Upload/Download with or without Container Action

This action helps in downloading or uploading files from Gdrive

### Example workflow

```yaml
steps:
- uses: actions/checkout@mian
- name: Run action
  id: myaction

  # example of your mandatory arguments here
  with:
    name: zip
    filename: *.zip
    folder_id: '#######'
    drive_id: '########'
    actions: 'upload' or 'download'
     credentials_file: ${{ secrets.CREDENTIALS_FILE }} #//credentials encoded string
