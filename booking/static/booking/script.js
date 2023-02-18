// nav menu functionality
const menuBtn = document.querySelector(".menu-toggle");
const closeBtn = document.querySelector(".close-btn");
const navlist = document.querySelector(".nav-list");

menuBtn.addEventListener("click", () => {
  navlist.classList.toggle("show-sidebar");
});

closeBtn.addEventListener("click", () => {
  navlist.classList.remove("show-sidebar");
});

// for csrf token
export const getCookie = (name) => {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    let cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      let cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
};
