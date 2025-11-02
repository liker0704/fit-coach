import { useState, useEffect, useRef, RefObject } from 'react';

export function useContainerSize<T extends HTMLElement = HTMLDivElement>(): [
  RefObject<T | null>,
  { width: number; height: number }
] {
  const ref = useRef<T | null>(null);
  const [size, setSize] = useState({ width: 0, height: 0 });

  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    const resizeObserver = new ResizeObserver((entries) => {
      for (const entry of entries) {
        const { width, height } = entry.contentRect;
        setSize({ width: Math.floor(width), height: Math.floor(height) });
      }
    });

    resizeObserver.observe(element);
    return () => resizeObserver.disconnect();
  }, []);

  return [ref, size];
}
