document.addEventListener('DOMContentLoaded', function () {
    const dropdown = document.querySelector('.dropdown');
    if (!dropdown) return;

    const dropdownToggle = dropdown.querySelector('a');
    const dropdownMenu = dropdown.querySelector('.dropdown-menu');

    let timeoutId;

    function showMenu() {
        clearTimeout(timeoutId);
        dropdownMenu.classList.add('show');
    }

    function hideMenu() {
        timeoutId = setTimeout(() => {
            dropdownMenu.classList.remove('show');
        }, 300);
    }

    dropdownToggle.addEventListener('mouseenter', showMenu);
    dropdownToggle.addEventListener('mouseleave', hideMenu);
    dropdownMenu.addEventListener('mouseenter', showMenu);
    dropdownMenu.addEventListener('mouseleave', hideMenu);

    // Prevent clicks inside dropdown menu from closing it
    dropdownMenu.addEventListener('click', function (e) {
        e.stopPropagation();
    });

    // Close dropdown if clicked outside
    document.addEventListener('click', function (e) {
        if (!dropdown.contains(e.target)) {
            dropdownMenu.classList.remove('show');
        }
    });
});

// Mobile menu toggle
const menuToggle = document.querySelector('.menu-toggle');
if (menuToggle) {
    menuToggle.addEventListener('click', function() {
        document.querySelector('.nav-links').classList.toggle('active');
    });
}
