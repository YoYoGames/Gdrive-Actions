# Python Container Action Template
[![Actions Status](https://github.com/jacobtomlinson/python-container-action/workflows/Lint/badge.svg)](https://github.com/jacobtomlinson/python-container-action/actions)
[![Actions Status](https://github.com/jacobtomlinson/python-container-action/workflows/Integration%20Test/badge.svg)](https://github.com/jacobtomlinson/python-container-action/actions)

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
