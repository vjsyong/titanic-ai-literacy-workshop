import { useEffect } from "react";
import confetti from "canvas-confetti";

/** Fire a short celebration burst across the screen. */
export function fireConfetti(colors?: string[]) {
  confetti({ particleCount: 180, spread: 110, origin: { y: 0.6 }, colors });

  const end = Date.now() + 2200;
  const frame = () => {
    confetti({
      particleCount: 3,
      angle: 60,
      spread: 55,
      origin: { x: 0, y: 0.7 },
      colors,
    });
    confetti({
      particleCount: 3,
      angle: 120,
      spread: 55,
      origin: { x: 1, y: 0.7 },
      colors,
    });
    if (Date.now() < end) requestAnimationFrame(frame);
  };
  frame();
}

/** Fire a short celebration the first time all checkpoints are done. */
export function useCompletionCelebration(allComplete: boolean) {
  useEffect(() => {
    if (!allComplete) return;
    if (sessionStorage.getItem("titanic-celebrated") === "1") return;
    sessionStorage.setItem("titanic-celebrated", "1");
    fireConfetti();
  }, [allComplete]);
}
