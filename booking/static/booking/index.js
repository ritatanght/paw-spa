import { getCookie } from "./script.js";

//review slider
const review = document.querySelectorAll(".review__item");
const prevBtn = document.querySelector(".review-prev");
const nextBtn = document.querySelector(".review-next");
let current = 0;

review[current].classList.add("current");
review[review.length - 1].classList.add("prev");
nextBtn.addEventListener("click", nextReview);
prevBtn.addEventListener("click", prevReview);

let intervalID = setInterval(nextReview, 6000);

function nextReview() {
  review[current - 1 < 0 ? review.length - 1 : current - 1].classList.remove(
    "prev"
  );
  review[current].classList.add("prev");
  review[current].classList.remove("current");
  // if the current review is larger than the amount of review, return to start of list
  current++;
  if (current == review.length) {
    current = 0;
  }
  review[current].classList.add("current");
  // Once the button is clicked, reset the interval
  resetInterval();
}

function prevReview() {
  review[current - 1 < 0 ? review.length - 1 : current - 1].classList.remove(
    "prev"
  );
  review[current].classList.remove("current");
  // if the current review is less than the amount of review, return to end of list
  current--;
  if (current < 0) {
    current = review.length - 1;
  }
  review[current - 1 < 0 ? review.length - 1 : current - 1].classList.add(
    "prev"
  );
  review[current].classList.add("current");
  // Once the button is clicked, reset the interval
  resetInterval();
}

function resetInterval() {
  clearInterval(intervalID);
  intervalID = setInterval(nextReview, 6000);
}

// comment form
const commentToggle = document.querySelector(".comment-toggle");
const comment_form = document.querySelector(".comment-form");
const commentBtn = document.querySelector(".comment-btn");
const comment = document.getElementById("comment");

commentToggle &&
  commentToggle.addEventListener("click", () => {
    comment_form.classList.toggle("show-form");
  });

// only able to submit comment when the textarea is not blank
comment &&
  comment.addEventListener("keyup", () => {
    console.log(comment.value.length);
    if (comment.value.length > 0) {
      commentBtn.classList.remove("disabled");
      commentBtn.disabled = false;
    } else {
      commentBtn.classList.add("disabled");
      commentBtn.disabled = true;
    }
  });

commentBtn &&
  commentBtn.addEventListener("click", () => {
    const username = document.querySelector(".username").textContent;

    if (comment.value.length > 0) {
      let csrftoken = getCookie("csrftoken");
      fetch("", {
        method: "POST",
        body: JSON.stringify({
          username: username,
          comment: comment.value,
        }),
        headers: { "X-CSRFToken": csrftoken },
      })
        .then((response) => response.json())
        .then((result) => {
          comment_form.parentElement.innerHTML = `<p>${result.message}<p>`;
        });
    }
  });
