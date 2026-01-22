document.addEventListener("DOMContentLoaded", () => {
    const body = document.querySelector('body'),
        sidebar = body.querySelector('nav'),
        toggle = body.querySelector(".toggle"),
        searchBtn = body.querySelector(".search-box");

    // Check if toggle exists before adding event listener
    if (toggle) {
        toggle.addEventListener("click", () => {
            sidebar.classList.toggle("close");
        });
    }

    // Check if searchBtn exists before adding event listener
    if (searchBtn) {
        searchBtn.addEventListener("click", () => {
            sidebar.classList.remove("close");
        });
    }

    // Load dark mode preference from localStorage on page load
    const darkModeEnabled = localStorage.getItem('darkMode') === 'enabled';
    if (darkModeEnabled) {
        body.classList.add('dark-mode');
        body.classList.add('dark');
    }
});
