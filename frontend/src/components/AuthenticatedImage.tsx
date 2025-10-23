"use client";

import { useState, useEffect } from 'react';
import { AuthService } from '@/services/auth.service';

interface AuthenticatedImageProps {
  src: string;
  alt: string;
  className?: string;
  style?: React.CSSProperties;
  onLoad?: () => void;
  onError?: (error: any) => void;
}

export default function AuthenticatedImage({ 
  src, 
  alt, 
  className, 
  style, 
  onLoad, 
  onError 
}: AuthenticatedImageProps) {
  const [imageSrc, setImageSrc] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchImage = async () => {
      try {
        setLoading(true);
        setError(null);

        // If it's already a blob URL or external URL, use it directly
        if (src.startsWith('blob:') || src.startsWith('http') && !src.includes('localhost')) {
          setImageSrc(src);
          setLoading(false);
          return;
        }

        // Fetch with authentication
        console.log('Fetching authenticated image:', src);
        const headers = AuthService.getAuthHeaders();
        console.log('Using auth headers:', headers);
        
        const response = await fetch(src, {
          headers,
        });

        if (!response.ok) {
          throw new Error(`Failed to load image: ${response.status} ${response.statusText}`);
        }

        const blob = await response.blob();
        const blobUrl = URL.createObjectURL(blob);
        setImageSrc(blobUrl);
        setLoading(false);
        onLoad?.();
      } catch (err) {
        console.error('Error loading authenticated image:', err);
        setError(err instanceof Error ? err.message : 'Failed to load image');
        setLoading(false);
        onError?.(err);
      }
    };

    if (src) {
      fetchImage();
    }

    // Cleanup blob URL on unmount
    return () => {
      if (imageSrc && imageSrc.startsWith('blob:')) {
        URL.revokeObjectURL(imageSrc);
      }
    };
  }, [src]);

  if (loading) {
    return (
      <div className={`flex items-center justify-center bg-gray-100 rounded ${className}`} style={style}>
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`flex items-center justify-center bg-red-50 border border-red-200 rounded p-4 ${className}`} style={style}>
        <div className="text-red-600 text-sm text-center">
          <div>Failed to load image</div>
          <div className="text-xs mt-1">{error}</div>
        </div>
      </div>
    );
  }

  return (
    <img
      src={imageSrc}
      alt={alt}
      className={className}
      style={style}
      onLoad={onLoad}
      onError={onError}
    />
  );
}
