/**
 * Confetti celebration utility for task completion
 */

export function triggerConfetti() {
  // Only run on client side
  if (typeof window === "undefined") return;

  const count = 100;
  const colors = ["#f97316", "#14b8a6", "#3b82f6", "#10b981", "#f59e0b"];

  for (let i = 0; i < count; i++) {
    createConfettiParticle(colors);
  }
}

function createConfettiParticle(colors: string[]) {
  const particle = document.createElement("div");
  const color = colors[Math.floor(Math.random() * colors.length)];

  // Random position and rotation
  const startX = Math.random() * window.innerWidth;
  const startY = Math.random() * window.innerHeight * 0.5;
  const rotation = Math.random() * 360;

  Object.assign(particle.style, {
    position: "fixed",
    width: "10px",
    height: "10px",
    backgroundColor: color,
    left: `${startX}px`,
    top: `${startY}px`,
    borderRadius: Math.random() > 0.5 ? "50%" : "0",
    pointerEvents: "none",
    zIndex: "9999",
    transform: `rotate(${rotation}deg)`,
  });

  document.body.appendChild(particle);

  // Animate
  const animation = particle.animate(
    [
      {
        transform: `translate(0, 0) rotate(${rotation}deg)`,
        opacity: 1,
      },
      {
        transform: `translate(${Math.random() * 200 - 100}px, ${window.innerHeight}px) rotate(${rotation + Math.random() * 360}deg)`,
        opacity: 0,
      },
    ],
    {
      duration: 2000 + Math.random() * 1000,
      easing: "cubic-bezier(0.25, 0.46, 0.45, 0.94)",
    }
  );

  animation.onfinish = () => {
    particle.remove();
  };
}
