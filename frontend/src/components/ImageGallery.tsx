"use client";

import { useState, useEffect } from 'react';
import { FaImage, FaDownload, FaTrash, FaEye, FaTimes } from 'react-icons/fa';

interface ImageItem {
  id: string;
  filename: string;
  url: string;
  thumbnail_url: string;
  created_at: number;
  size: number;
  prompt?: string;
  model?: string;
  generation_type?: string;
  timestamp?: string;
}

interface ImageGalleryProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function ImageGallery({ isOpen, onClose }: ImageGalleryProps) {
  const [images, setImages] = useState<ImageItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedImage, setSelectedImage] = useState<ImageItem | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      fetchImages();
    }
  }, [isOpen]);

  const fetchImages = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/v1/images/gallery', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch images');
      }

      const data = await response.json();
      setImages(data.gallery || []);
    } catch (err) {
      console.error('Error fetching images:', err);
      setError('Failed to load images');
    } finally {
      setLoading(false);
    }
  };

  const deleteImage = async (filename: string) => {
    try {
      const response = await fetch(`/api/v1/images/${filename}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to delete image');
      }

      // Remove from local state
      setImages(images.filter(img => img.filename !== filename));
      
      // Close modal if this image was selected
      if (selectedImage?.filename === filename) {
        setSelectedImage(null);
      }
    } catch (err) {
      console.error('Error deleting image:', err);
      setError('Failed to delete image');
    }
  };

  const downloadImage = (imageUrl: string, filename: string) => {
    const link = document.createElement('a');
    link.href = imageUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const formatDate = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-6xl w-full mx-4 max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div className="flex items-center space-x-2">
            <FaImage className="text-blue-600" />
            <h2 className="text-xl font-semibold text-gray-900">Image Gallery</h2>
            <span className="text-sm text-gray-500">({images.length} images)</span>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 p-2"
          >
            <FaTimes />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
          {loading && (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <span className="ml-2 text-gray-600">Loading images...</span>
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
              <p className="text-red-800">{error}</p>
              <button
                onClick={fetchImages}
                className="mt-2 text-red-600 hover:text-red-800 text-sm underline"
              >
                Try again
              </button>
            </div>
          )}

          {!loading && !error && images.length === 0 && (
            <div className="text-center py-12">
              <FaImage className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <p className="text-gray-600">No images generated yet</p>
              <p className="text-sm text-gray-500 mt-2">
                Use the Gemini image tools to generate your first image!
              </p>
            </div>
          )}

          {!loading && !error && images.length > 0 && (
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {images.map((image) => (
                <div
                  key={image.id}
                  className="bg-white border rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-shadow"
                >
                  <div className="aspect-square relative">
                    <img
                      src={image.url}
                      alt={image.prompt || 'Generated image'}
                      className="w-full h-full object-cover cursor-pointer"
                      onClick={() => setSelectedImage(image)}
                    />
                    <div className="absolute inset-0 bg-black bg-opacity-0 hover:bg-opacity-20 transition-opacity flex items-center justify-center opacity-0 hover:opacity-100">
                      <FaEye className="text-white text-xl" />
                    </div>
                  </div>
                  
                  <div className="p-3">
                    <div className="text-xs text-gray-600 mb-2">
                      {formatDate(image.created_at)}
                    </div>
                    
                    {image.prompt && (
                      <div className="text-xs text-gray-800 mb-2 line-clamp-2">
                        <strong>Prompt:</strong> {image.prompt}
                      </div>
                    )}
                    
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-500">
                        {formatFileSize(image.size)}
                      </span>
                      
                      <div className="flex space-x-1">
                        <button
                          onClick={() => downloadImage(image.url, image.filename)}
                          className="p-1 text-gray-400 hover:text-blue-600 transition-colors"
                          title="Download"
                        >
                          <FaDownload className="text-xs" />
                        </button>
                        <button
                          onClick={() => deleteImage(image.filename)}
                          className="p-1 text-gray-400 hover:text-red-600 transition-colors"
                          title="Delete"
                        >
                          <FaTrash className="text-xs" />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Image Modal */}
      {selectedImage && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-60">
          <div className="max-w-4xl max-h-[90vh] bg-white rounded-lg overflow-hidden">
            <div className="flex items-center justify-between p-4 border-b">
              <h3 className="font-semibold text-gray-900">Image Details</h3>
              <button
                onClick={() => setSelectedImage(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                <FaTimes />
              </button>
            </div>
            
            <div className="p-4">
              <img
                src={selectedImage.url}
                alt={selectedImage.prompt || 'Generated image'}
                className="max-w-full max-h-[60vh] mx-auto rounded-lg"
              />
              
              <div className="mt-4 space-y-2 text-sm">
                <div><strong>Filename:</strong> {selectedImage.filename}</div>
                <div><strong>Created:</strong> {formatDate(selectedImage.created_at)}</div>
                <div><strong>Size:</strong> {formatFileSize(selectedImage.size)}</div>
                {selectedImage.prompt && (
                  <div><strong>Prompt:</strong> {selectedImage.prompt}</div>
                )}
                {selectedImage.model && (
                  <div><strong>Model:</strong> {selectedImage.model}</div>
                )}
                {selectedImage.generation_type && (
                  <div><strong>Type:</strong> {selectedImage.generation_type}</div>
                )}
              </div>
              
              <div className="flex space-x-2 mt-4">
                <button
                  onClick={() => downloadImage(selectedImage.url, selectedImage.filename)}
                  className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <FaDownload />
                  <span>Download</span>
                </button>
                <button
                  onClick={() => deleteImage(selectedImage.filename)}
                  className="flex items-center space-x-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                >
                  <FaTrash />
                  <span>Delete</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
