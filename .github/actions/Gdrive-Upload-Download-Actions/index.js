const fs = require('fs');
const { google } = require('googleapis');
const { promisify } = require('util');
const readline = require('readline');

// Load credentials from a JSON file
const credentialsFile = 'credentials.json'; // Path to your credentials file
const credentials = JSON.parse(fs.readFileSync(credentialsFile));

// Scope for Google Drive API
const SCOPES = ['https://www.googleapis.com/auth/drive.file'];

// Create an OAuth2 client with the given credentials
const { client_secret, client_id, redirect_uris } = credentials.installed;
const oAuth2Client = new google.auth.OAuth2(
  client_id, client_secret, redirect_uris[0]
);

// Set the token if available, otherwise get a new one
const tokenFile = 'token.json'; // Path to your token file
const readFileAsync = promisify(fs.readFile);
const writeFileAsync = promisify(fs.writeFile);
let token;
readFileAsync(tokenFile)
  .then(data => {
    token = JSON.parse(data);
    oAuth2Client.setCredentials(token);
    main();
  })
  .catch(err => {
    getAccessToken(oAuth2Client)
      .then(token => {
        writeFileAsync(tokenFile, JSON.stringify(token))
          .then(() => {
            console.log('Token stored to', tokenFile);
            main();
          })
          .catch(err => console.error('Error storing token:', err));
      })
      .catch(err => console.error('Error retrieving access token:', err));
  });

// Create a new Google Drive API client
const drive = google.drive({ version: 'v3', auth: oAuth2Client });

// Main function to upload or download files
async function main() {
  // Command line arguments
  const args = process.argv.slice(2);
  const [action, filename, name, driveId, folderId, overwrite, mimeType] = args;

  try {
    if (action === 'upload') {
      const fileMetadata = { name, parents: [driveId] };
      const media = {
        mimeType,
        body: fs.createReadStream(filename),
      };

      const res = await drive.files.create({
        resource: fileMetadata,
        media,
        fields: 'id',
        supportsAllDrives: true,
      });
      console.log('Upload completed. File ID:', res.data.id);
    } else if (action === 'download') {
      const res = await drive.files.get({
        fileId: folderId,
        alt: 'media',
      }, { responseType: 'stream' });

      const dest = fs.createWriteStream(filename);
      res.data
        .on('end', () => console.log('Download completed. File saved to', filename))
        .on('error', err => console.error('Download failed:', err))
        .pipe(dest);
    } else {
      console.error('Invalid action. Please specify "upload" or "download".');
    }
  } catch (err) {
    console.error('An error occurred:', err);
  }
}

// Function to get an OAuth2 access token
async function getAccessToken(oAuth2Client) {
  return new Promise((resolve, reject) => {
    const authUrl = oAuth2Client.generateAuthUrl({
      access_type: 'offline',
      scope: SCOPES,
    });
    console.log('Authorize this app by visiting this URL:', authUrl);
    
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
    });
    
    rl.question('Enter the code from that page here: ', code => {
      rl.close();
      oAuth2Client.getToken(code, (err, token) => {
        if (err) {
          console.error('Error retrieving access token:', err);
          reject(err);
        }
        resolve(token);
      });
    });
  });
}
