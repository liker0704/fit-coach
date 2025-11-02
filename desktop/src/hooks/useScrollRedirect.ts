import { useEffect } from 'react';

/**
 * Redirects all wheel scroll events to the scrollable container with smooth animation,
 * even when the mouse is outside the container.
 * This allows scrolling the page content when hovering over sidebar or other areas.
 */
export function useScrollRedirect() {
  useEffect(() => {
    // Check if user prefers reduced motion
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    let targetScroll = 0;
    let currentScroll = 0;
    let animationFrameId: number | null = null;

    const animate = () => {
      // Get fresh reference to container on each animation frame
      const scrollContainer = document.querySelector('main .overflow-y-auto') as HTMLElement;
      if (!scrollContainer) {
        animationFrameId = null;
        return;
      }

      // Linear interpolation (lerp) for smooth scrolling
      // Higher value (0.15) = faster, Lower value (0.1) = smoother
      const easingFactor = prefersReducedMotion ? 1 : 0.1;

      currentScroll += (targetScroll - currentScroll) * easingFactor;

      // Apply scroll position
      scrollContainer.scrollTop = currentScroll;

      // Continue animation if there's still distance to cover
      if (Math.abs(targetScroll - currentScroll) > 0.5) {
        animationFrameId = requestAnimationFrame(animate);
      } else {
        // Snap to final position
        scrollContainer.scrollTop = targetScroll;
        currentScroll = targetScroll;
        animationFrameId = null;
      }
    };

    const handleWheel = (event: WheelEvent) => {
      // Get fresh reference to container (fixes stale reference after route change)
      const scrollContainer = document.querySelector('main .overflow-y-auto') as HTMLElement;
      if (!scrollContainer) return;

      // Prevent default body scroll
      event.preventDefault();

      // Update target scroll position
      targetScroll += event.deltaY;

      // Clamp to valid scroll range
      const maxScroll = scrollContainer.scrollHeight - scrollContainer.clientHeight;
      targetScroll = Math.max(0, Math.min(targetScroll, maxScroll));

      // Start animation if not already running
      if (animationFrameId === null) {
        currentScroll = scrollContainer.scrollTop;
        targetScroll = currentScroll + event.deltaY;
        targetScroll = Math.max(0, Math.min(targetScroll, maxScroll));
        animationFrameId = requestAnimationFrame(animate);
      }
    };

    // Add wheel event listener with passive: false AND capture: true
    // capture: true means we intercept events in capture phase (earlier than bubble phase)
    window.addEventListener('wheel', handleWheel, { passive: false, capture: true });

    // Also add on document for redundancy
    document.addEventListener('wheel', handleWheel, { passive: false, capture: true });

    return () => {
      window.removeEventListener('wheel', handleWheel);
      document.removeEventListener('wheel', handleWheel);
      if (animationFrameId !== null) {
        cancelAnimationFrame(animationFrameId);
      }
    };
  }, []);
}
