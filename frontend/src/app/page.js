'use client';
import { useState, useCallback } from 'react';
import Image from "next/image";

export default function Home() {
  const [isDragging, setIsDragging] = useState(false);
  const [uploadStatus, setUploadStatus] = useState('');

  const handleUpload = async (file) => {
    try {
      // Get pre-signed URL
      const response = await fetch('/api/upload', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ fileName: file.name })
      });
      const { url, fileName } = await response.json();

      // Upload file to S3
      const uploadResponse = await fetch(url, {
        method: 'PUT',
        body: file,
        headers: { 'Content-Type': 'application/pdf' }
      });

      if (uploadResponse.ok) {
        setUploadStatus('Upload successful!');
      } else {
        setUploadStatus('Upload failed.');
      }
    } catch (error) {
      console.error('Error uploading file:', error);
      setUploadStatus('Upload failed.');
    }
  };

  const onDragOver = useCallback((e) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const onDragLeave = useCallback((e) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const onDrop = useCallback((e) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file && file.type === 'application/pdf') {
      handleUpload(file);
    } else {
      setUploadStatus('Please upload a PDF file.');
    }
  }, []);

  return (
    <div className="min-h-screen p-8">
      <h1 className="text-3xl font-bold mb-8">Talkify</h1>
      
      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
          ${isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300'}`}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onDrop={onDrop}
      >
        <div className="mb-4">
          <p className="text-lg">Drag and drop your PDF file here, or</p>
          <label className="inline-block bg-blue-500 text-white px-4 py-2 rounded mt-2 cursor-pointer">
            Browse Files
            <input
              type="file"
              accept=".pdf"
              className="hidden"
              onChange={(e) => {
                const file = e.target.files[0];
                if (file) handleUpload(file);
              }}
            />
          </label>
        </div>
        {uploadStatus && (
          <p className={uploadStatus.includes('successful') ? 'text-green-500' : 'text-red-500'}>
            {uploadStatus}
          </p>
        )}
      </div>
    </div>
  );
}
