document.addEventListener("DOMContentLoaded", function () {
    const navHomeTab = document.getElementById("nav-home-tab");
    const navProfileTab = document.getElementById("nav-profile-tab");
    const featuresSection = document.getElementById("Features");
    const documentationSection = document.getElementById("Documentation");

    featuresSection.style.display = "block";
    documentationSection.style.display = "none";
    navHomeTab.classList.add("active");

    navHomeTab.addEventListener("click", function () {
        featuresSection.style.display = "block";
        documentationSection.style.display = "none";
        navHomeTab.classList.add("active");
        navProfileTab.classList.remove("active");
    });
    
    navProfileTab.addEventListener("click", function () {
        documentationSection.style.display = "block";
        featuresSection.style.display = "none";
        navProfileTab.classList.add("active");
        navHomeTab.classList.remove("active");
    });
});

function toggleLed(state) {
    fetch(`/?led=${state}`)
        .then(response => response.text())
        .then(data => {
            console.log(`LED ${state.toUpperCase()} - Răspuns server: ${data}`);
        })
        .catch(error => {
            console.error('Eroare la trimiterea cererii pentru LED:', error);
        });
}

function setRgbLedColor(color) {
    fetch(`/?rgb=${color.substring(1)}`)
        .then(response => response.text())
        .then(data => {
            console.log(`RGB LED setat la culoarea ${color} - Răspuns server: ${data}`);
        })
        .catch(error => {
            console.error('Eroare la trimiterea culorii RGB:', error);
        });
}

hljs.highlightAll();