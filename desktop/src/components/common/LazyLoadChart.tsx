import React, { useState, useRef, useEffect, ReactNode } from 'react';

interface LazyLoadChartProps {
  children: ReactNode;
  height: number; // Required to prevent layout shift
  rootMargin?: string; // Preload distance
  threshold?: number;
}

export const LazyLoadChart: React.FC<LazyLoadChartProps> = ({
  children,
  height,
  rootMargin = '200px', // Research recommendation: preload 200px before visible
  threshold = 0.01,
}) => {
  const [isInView, setIsInView] = useState(false);
  const placeholderRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsInView(true);
          // Stop observing once visible (performance optimization)
          if (placeholderRef.current) {
            observer.unobserve(placeholderRef.current);
          }
        }
      },
      {
        root: null, // Observe viewport
        rootMargin,
        threshold,
      }
    );

    const currentRef = placeholderRef.current;
    if (currentRef) {
      observer.observe(currentRef);
    }

    // Cleanup
    return () => {
      if (currentRef) {
        observer.unobserve(currentRef);
      }
      observer.disconnect();
    };
  }, [rootMargin, threshold]);

  return isInView ? (
    <>{children}</>
  ) : (
    <div
      ref={placeholderRef}
      style={{ height: `${height}px`, width: '100%' }}
      aria-busy="true"
      className="animate-pulse bg-gray-100 rounded-lg flex items-center justify-center"
    >
      <div className="text-gray-400 text-sm">Loading chart...</div>
    </div>
  );
};
