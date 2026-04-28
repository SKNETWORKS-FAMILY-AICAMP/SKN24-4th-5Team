function setupProfileMenus(root = document) {
    const closeMenus = () => {
        root.querySelectorAll(".profile-menu.is-open").forEach((menu) => {
            menu.classList.remove("is-open");
            menu.querySelector(".profile-menu__button")?.setAttribute("aria-expanded", "false");
        });
    };

    root.querySelectorAll(".profile-menu").forEach((menu) => {
        const button = menu.querySelector(".profile-menu__button");

        if (!button) {
            return;
        }

        button.addEventListener("click", (event) => {
            event.stopPropagation();
            const isOpen = menu.classList.toggle("is-open");
            button.setAttribute("aria-expanded", String(isOpen));
        });
    });

    document.addEventListener("click", closeMenus);
    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            closeMenus();
        }
    });
}

document.addEventListener("DOMContentLoaded", () => {
    setupProfileMenus();
});
