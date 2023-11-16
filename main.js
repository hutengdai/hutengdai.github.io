document.addEventListener('DOMContentLoaded', function() {
    var navHamburger = document.querySelector('.nav-hamburger');
    var navMenu = document.querySelector('.nav-menu');

    navHamburger.addEventListener('click', function() {
        navMenu.style.display = navMenu.style.display === 'block' ? 'none' : 'block';
    });

    window.addEventListener('scroll', function() {
        navMenu.style.display = 'none'; // Hide menu on scroll
    });

    // Close the hamburger menu when a link is clicked
    document.querySelectorAll('.nav-menu a').forEach(function(link) {
        link.addEventListener('click', function() {
            navMenu.style.display = 'none';
        });
    });
});
