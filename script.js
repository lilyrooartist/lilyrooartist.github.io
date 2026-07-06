document.documentElement.classList.add("js-enabled");

const revealItems = document.querySelectorAll(".reveal");

if (revealItems.length > 0) {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("visible");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.2 }
  );

  revealItems.forEach((item) => observer.observe(item));
}

const shareButtons = document.querySelectorAll(".share-button");

shareButtons.forEach((button) => {
  const originalLabel = button.textContent;

  button.addEventListener("click", async () => {
    const shareUrl = button.dataset.shareUrl || window.location.href;
    const shareTitle = button.dataset.shareTitle || document.title;
    const shareText = button.dataset.shareText || "";

    try {
      if (navigator.share) {
        await navigator.share({
          title: shareTitle,
          text: shareText,
          url: shareUrl,
        });
        return;
      }

      const clipboardText = [shareText, shareUrl].filter(Boolean).join("\n");
      await navigator.clipboard.writeText(clipboardText);
      button.textContent = "Copied";
      window.setTimeout(() => {
        button.textContent = originalLabel;
      }, 1800);
    } catch (error) {
      if (error && error.name === "AbortError") return;
      button.textContent = "Copy Failed";
      window.setTimeout(() => {
        button.textContent = originalLabel;
      }, 1800);
    }
  });
});
