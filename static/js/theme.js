let dark = "DARK".toLowerCase();
let light = "LIGHT".toLowerCase();



function toggleIcon(body) {
    let moonIcon = `<span class="material-icons-round">nightlight</span>`;
    let sunIcon = `<span class="material-icons-round">light_mode</span>`;

    if (body.classList.contains(dark)) {
        themeToggler.innerHTML = sunIcon
        sessionStorage.setItem("theme", dark);
    } else {
        themeToggler.innerHTML = moonIcon;
        sessionStorage.setItem("theme", light);
    }
}

function toggleTheme() {
    let body = document.body

    body.classList.toggle(dark);
    toggleIcon(body);
}

function randomHexColor() {
    let randomNumber = Math.floor(Math.random() * 0xFFFFFF);
    let hexString = '#' + randomNumber.toString(16).padStart(6, '0');
    return hexString;
}

function randomPosition(element) {
    // Get the screen width and height.
    let screenWidth = window.innerWidth;
    let screenHeight = window.innerHeight;

    // Get the element's width and height.
    let elementWidth = element.offsetWidth;
    let elementHeight = element.offsetHeight;

    // Calculate the random position for the element.
    let x = Math.floor(Math.random() * (screenWidth - elementWidth));
    let y = Math.floor(Math.random() * (screenHeight - elementHeight));

    // Generate a random color.
    let randomColor = randomHexColor();

    // Set the element's position.
    element.style.left = x + 'px';
    element.style.top = y + 'px';

    // Set the element's background color.
    element.style.backgroundColor = randomColor;
}

function toggleSidebarAndNavbar() {
    document.querySelector(".side-bar").classList.toggle("side-bar-show");
    document.querySelector("#navbar")?.classList.toggle("slid-from-top-hover");
}


document.addEventListener("DOMContentLoaded", () => {
    let body = document.body;
    let themeToggler = document.getElementById("themeToggler");
    let bluredElements = document.querySelectorAll(".blur");

    body.classList.add(sessionStorage.getItem("theme"))
    toggleIcon(body)

    themeToggler.addEventListener("click", () => {
        themeToggler.classList.toggle("active")
        toggleTheme();
    });

    // Changing .blur position randomly
    bluredElements?.forEach((e) => {
        randomPosition(e)
    });
    // side-bar
    document.getElementById("sideBarToggle")?.addEventListener("click", () => {
        toggleSidebarAndNavbar();
    })
});

