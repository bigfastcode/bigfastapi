// let menu = document.querySelector("#menu-icon");
// let navlinks = document.querySelector(".navlinks");

// menu.addEventListener("click", function () {
//     navlinks.classList.toggle("active");
// });

// window.onscroll = () => {
//     navlinks.classList.remove("active")
// }

const hamburger = document.querySelector(".hamburger");
const navLinks = document.querySelector(".nav-links");
const links = document.querySelectorAll(".nav-links li");

hamburger.addEventListener('click', ()=>{
   //Animate Links
    navLinks.classList.toggle("open");
    links.forEach(link => {
        link.classList.toggle("fade");
    });

    //Hamburger Animation
    hamburger.classList.toggle("toggle");
});