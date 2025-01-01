// File selection
const fileInput = document.getElementById('fileInput');
fileInput.addEventListener('change', () => {
  const file = fileInput.files[0];
  const reader = new FileReader();

  reader.onload = (e) => {
    const fileData = e.target.result; 

    // Send file data to server (e.g., using Fetch API)
    fetch('/upload', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ filename: file.name, data: fileData }) 
    })
    .then(response => response.json())
    .then(data => {
      // Handle server response (e.g., display download link)
      const downloadLink = document.getElementById('downloadLink');
      downloadLink.href = `/download/${data.fileId}`; 
      downloadLink.textContent = "Download"; 
    })
    .catch(error => console.error('Error uploading file:', error));
  };

  reader.readAsDataURL(file); 
});

// server-side (simplified - Node.js with Express and a cloud storage library like Firebase)

const express = require('express');
const app = express();
const { initializeApp, getStorage } = require('firebase/app');
const { getDownloadURL, ref, uploadBytesResumable } = require('firebase/storage');

// Initialize Firebase (replace with your actual credentials)
const firebaseConfig = {
  // ... your Firebase config ...
};
const app = initializeApp(firebaseConfig);
const storage = getStorage(app);

app.use(express.json());

app.post('/upload', async (req, res) => {
  try {
    const { filename, data } = req.body; 
    const storageRef = ref(storage, `files/${filename}`); 

    // Convert data URL back to Blob
    const byteString = atob(data.split(',')[1]);
    const mimeString = data.split(',')[0].split(':')[1].split(';')[0];
    const ab = new ArrayBuffer(byteString.length);
    const ia = new Uint8Array(ab);
    for (let i = 0; i < byteString.length; i++) {
      ia[i] = byteString.charCodeAt(i);
    }
    const blob = new Blob([ab], { type: mimeString });

    // Upload to Firebase Storage
    const uploadTask = uploadBytesResumable(storageRef, blob);

    uploadTask.on('state_changed', 
      (snapshot) => {
        // Progress updates
      }, 
      (error) => {
        // Handle errors
      }, 
      () => {
        // Upload complete
        getDownloadURL(uploadTask.snapshot.ref).then((downloadURL) => {
          res.json({ fileId: downloadURL }); 
        });
      }
    );

  } catch (error) {
    console.error('Error uploading file:', error);
    res.status(500).send('Error uploading file');
  }
});

app.get('/download/:fileId', (req, res) => {
  res.redirect(req.params.fileId); 
});

app.listen(3000, () => {
  console.log('Server listening on port 3000');
});

// Important Notes:

/* **Security:** This is a simplified example. For production, implement proper authentication and authorization to control file access.
* **Error Handling:** Enhance error handling on both client and server sides.
* **Cloud Storage:** Replace Firebase with your preferred cloud storage solution (AWS S3, Google Cloud Storage, etc.).
* **Data URL Limitations:** Data URLs can have size limitations. For larger files, consider direct file uploads.
* **Client-Side Libraries:** Use a dedicated client-side library to simplify file uploads and downloads.
* **Scalability:** Consider using a load balancer and a more robust server architecture for high traffic.

This provides a basic framework. 
