(function () {
  document.addEventListener("DOMContentLoaded", function () {
    const theme = localStorage.getItem("theme");

    if (theme) {
      document.documentElement.setAttribute("data-bs-theme", theme);
    }

    function toggleTheme() {
      const currentTheme =
        document.documentElement.getAttribute("data-bs-theme");
      const newTheme = currentTheme === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-bs-theme", newTheme);
      localStorage.setItem("theme", newTheme);

      // Update the theme icon
      const themeIcon = document.querySelector("#theme-toggle i");
      themeIcon.classList.toggle("bi-sun", newTheme === "dark");
      themeIcon.classList.toggle("bi-moon", newTheme === "light");
    }

    window.toggleTheme = toggleTheme;
  });
})();
