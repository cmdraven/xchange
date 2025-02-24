import os
import hashlib
import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import firebase_admin
from firebase_admin import credentials, storage

# Initialize Firebase (replace with your credentials and bucket name)
try:
    cred = credentials.Certificate("path/to/your/serviceAccountKey.json")  # Replace with your path
    firebase_admin.initialize_app(cred, {'storageBucket': 'your-bucket-name.appspot.com'}) # Replace with your bucket name
except Exception as e:
    print(f"Firebase Initialization Error: {e}")
    messagebox.showerror("Firebase Error", f"Failed to initialize Firebase: {e}")

class SilkRouteGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SilkRoute File Market")
        self.base_directory = "silkroute_files"
        if not os.path.exists(self.base_directory):
            os.makedirs(self.base_directory)

        self.create_widgets()

    def create_widgets(self):
        # Upload Button
        self.upload_button = tk.Button(self.root, text="Upload File", command=self.upload_file)
        self.upload_button.pack(pady=10)

        # Download Button
        self.download_button = tk.Button(self.root, text="Download File", command=self.download_file)
        self.download_button.pack(pady=10)

        # Delete Button
        self.delete_button = tk.Button(self.root, text="Delete File", command=self.delete_file)
        self.delete_button.pack(pady=10)

        # List Files Button
        self.list_button = tk.Button(self.root, text="List Files", command=self.list_files)
        self.list_button.pack(pady=10)

        # File ID Entry
        self.file_id_label = tk.Label(self.root, text="File ID:")
        self.file_id_label.pack()
        self.file_id_entry = tk.Entry(self.root)
        self.file_id_entry.pack()

        # Output Text Area
        self.output_text = scrolledtext.ScrolledText(self.root, height=10, width=60)
        self.output_text.pack(pady=10)

    def _generate_file_id(self, filename, content):
        file_hash = hashlib.sha256(content).hexdigest()
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        return f"{timestamp}-{file_hash[:8]}-{filename}"

    def upload_file(self):
        filepath = filedialog.askopenfilename()
        if filepath:
            try:
                with open(filepath, "rb") as f:
                    content = f.read()
                filename = os.path.basename(filepath)
                file_id = self._generate_file_id(filename, content)
                file_path = os.path.join(self.base_directory, file_id)
                with open(file_path, "wb") as f:
                    f.write(content)
                bucket = storage.bucket()
                blob = bucket.blob(file_id)
                blob.upload_from_filename(file_path)
                self.output_text.insert(tk.END, f"File '{filename}' uploaded with ID: {file_id}\n")
            except Exception as e:
                messagebox.showerror("Error", f"Error uploading file: {e}")

    def download_file(self):
        file_id = self.file_id_entry.get()
        if file_id:
            try:
                bucket = storage.bucket()
                blob = bucket.blob(file_id)
                file_path = os.path.join(self.base_directory, file_id)
                blob.download_to_filename(file_path)
                self.output_text.insert(tk.END, f"File '{file_id}' downloaded.\n")
            except Exception as e:
                messagebox.showerror("Error", f"Error downloading file: {e}")

    def delete_file(self):
        file_id = self.file_id_entry.get()
        if file_id:
            try:
                bucket = storage.bucket()
                blob = bucket.blob(file_id)
                blob.delete()
                os.remove(os.path.join(self.base_directory, file_id))
                self.output_text.insert(tk.END, f"File '{file_id}' deleted.\n")
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting file: {e}")

    def list_files(self):
        try:
            bucket = storage.bucket()
            blobs = bucket.list_blobs()
            self.output_text.delete(1.0, tk.END) #Clear the text widget
            for blob in blobs:
                self.output_text.insert(tk.END, f"- {blob.name}\n")
        except Exception as e:
            messagebox.showerror("Error", f"Error listing files: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SilkRouteGUI(root)
    root.mainloop()
