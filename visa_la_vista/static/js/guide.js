document.addEventListener("DOMContentLoaded", () => {
  const tabButtons = document.querySelectorAll("[data-guide-target]");
  const panels = document.querySelectorAll("[data-guide-panel]");

  if (!tabButtons.length || !panels.length) {
    return;
  }

  const activateGuide = (target) => {
    tabButtons.forEach((button) => {
      const isActive = button.dataset.guideTarget === target;
      button.classList.toggle("is-active", isActive);
      button.setAttribute("aria-selected", String(isActive));
    });

    panels.forEach((panel) => {
      const isActive = panel.dataset.guidePanel === target;
      panel.classList.toggle("is-active", isActive);
      panel.hidden = !isActive;
    });
  };

  tabButtons.forEach((button) => {
    button.addEventListener("click", () => {
      activateGuide(button.dataset.guideTarget);
    });
  });
});
