import { getCookie } from "./script.js";

// toggle add pet form
const add_btn = document.querySelector(".add-pet");
const pet_form = document.querySelector(".pet-form");
let csrftoken = getCookie("csrftoken");

add_btn.addEventListener("click", () => {
  pet_form.classList.toggle("show-form");
});

// del pet record
const del_btn = document.querySelectorAll(".del-btn");
del_btn &&
  del_btn.forEach((btn) => {
    btn.addEventListener("click", (e) => confirmDel(e.target.parentElement));
  });

function confirmDel(pet) {
  const petItem = pet.innerHTML;
  pet.innerHTML =
    '<small>All the related records for this pet will be deleted.</small><p>Are you sure?<p><div class="btn-group flex"><button class="btn btn-inverted" id="yes">Yes</button><button class="btn" id="no">No</button></div>';
  document.getElementById("yes").addEventListener("click", () => {
    const username = document.querySelector(".username").textContent;

    fetch("/profile", {
      method: "DELETE",
      body: JSON.stringify({
        pet: pet.id,
      }),
      headers: { "X-CSRFToken": csrftoken },
    }).then((response) => {
      if (response.ok) {
        pet.style.background = "var(--clr-secondary)";
        pet.style.opacity = "0";
        pet.innerHTML = "<p>Deleted<p>";
        setTimeout(() => {
          pet.remove();
          location.reload();
        }, 1100);
      }
    });
  });
  document.getElementById("no").addEventListener("click", () => {
    pet.innerHTML = petItem;
    pet
      .querySelector(".del-btn")
      .addEventListener("click", (e) => confirmDel(e.target.parentElement));
  });
}

// Edit phone and email
const editBtn = document.querySelectorAll(".edit-btn");

editBtn.forEach((btn) => {
  btn.addEventListener("click", (e) => updateField(e.target));
});

function updateField(edit_btn) {
  const field = edit_btn.previousElementSibling;
  let field_value = field.textContent;

  edit_btn.style.display = "none";

  if (field.id === "phone") {
    field_value = field_value.replace(/\s|\(|\)|\-/g, ""); // remove the meta characters in the field
    field.innerHTML = `<input type='tel' name='phone' pattern='[0-9]{10}' value='${field_value}' autofocus> <button class="btn save-btn">Save</button>`;
  } else {
    field.innerHTML = `<input type='email' name='email' value='${field_value}' autofocus>  <button class="btn save-btn">Save</button>`;
  }
  field
    .querySelector(".save-btn")
    .addEventListener("click", () => updateDatabase(field));
}

function updateDatabase(field) {
  let value = field.querySelector("input").value;
  fetch("/profile", {
    method: "PUT",
    body: JSON.stringify({
      field: field.id,
      value: value,
    }),
    headers: { "X-CSRFToken": csrftoken },
  })
    .then((response) => {
      if (response.ok) {
        // if it is the phone field, resume the phone number format
        field.innerHTML = `<span id="${field.id}">${
          field.id === "phone"
            ? "(" +
              value.slice(0, 3) +
              ") " +
              value.slice(3, 6) +
              "-" +
              value.slice(6)
            : value
        }</span>`;
        field.nextElementSibling.style.display = "inline-block";
      } else {
        return response.json();
      }
    })
    .then((result) => {
      if (result.message) {
        alert(result.message);
      }
    });
}

// Appointment details in modal
const details = document.querySelectorAll(".details-btn");
const modal = document.querySelector(".modal");

details.forEach((btn) => {
  btn.addEventListener("click", (e) => {
    modal.classList.add("show-modal");
    // reset the display to be appointment details
    modalDisplay("text");

    // close modal
    document
      .querySelector(".modal__close-btn")
      .addEventListener("click", () => {
        modal.classList.remove("show-modal");
      });

    //fetch and fill content for modal
    fetch(`/appointment/${e.target.id}`)
      .then((response) => response.json())
      .then((result) => {
        if (result.error) {
          modal.querySelector(
            ".modal__text"
          ).innerHTML = `<h4 class='center'>${result.error}</h4>`;
        } else {
          const { id, dog, date, time, service, add_ons, created } = result;

          if (add_ons === "None") {
            document.getElementById(
              "add-ons"
            ).innerHTML = `<li>${add_ons}</li>`;
          } else {
            let addOnsArr = add_ons.split(",");
            let list = "";
            for (let i = 0; i < addOnsArr.length; i++) {
              list = list + `<li>${addOnsArr[i]}</li>`;
            }
            document.getElementById("add-ons").innerHTML = list;
          }
          document.getElementById("ref").textContent = id
            .toString()
            .padStart(5, "0");
          document.getElementById(
            "datetime"
          ).textContent = `${time} on ${date}`;
          document.getElementById("dog").textContent = dog;
          document.getElementById("service").textContent = service;
          document.getElementById("created").textContent = created;

          document
            .querySelector(".booking__btn-edit")
            .addEventListener("click", () => editBooking(result));
          document
            .querySelector(".booking__btn-cancel")
            .addEventListener("click", () => cancelBooking(id));
        }
      });
  });
});

function editBooking(fields_value) {
  modalDisplay("form");

  // add-ons checkboxes behaviour - none box cannot be checked when other boxes are checked
  const checkbox = document.querySelectorAll("input[type=checkbox]");
  checkbox.forEach((box) => {
    box.addEventListener("change", (e) => {
      // when the None box is checked
      if (e.target.checked && e.target.value === "0") {
        checkbox.forEach((checkedbox) => {
          console.log(checkedbox);
          if (checkedbox.value !== "0") {
            checkedbox.checked = false;
          }
        });
      } else if (
        e.target.checked &&
        e.target.value !== "0" &&
        checkbox[0].checked
      ) {
        checkbox[0].checked = false;
      }
    });
  });

  // prepopulate form with record from database
  for (const property in fields_value) {
    let field = document.getElementById(`id_${property}`);
    if (field) {
      if (field.tagName === "SELECT") {
        // applicable for pet name, time, and service
        const options = field.querySelectorAll("option");
        options.forEach((option) => {
          if (option.innerText === fields_value[property]) {
            option.selected = true;
          }
        });
      } else if (field.tagName === "INPUT") {
        // meaning it is a date field
        field.value = new Date(fields_value[property]).toLocaleDateString(
          "en-CA",
          { year: "numeric", month: "2-digit", day: "2-digit" }
        );
      } else {
        // add_ons services
        const list = fields_value["add_ons_list"];
        const checkboxes = field.querySelectorAll("input");
        // uncheck all the boxes first, then check the checkboxes according to record
        checkboxes.forEach((box) => {
          box.checked = false;
        });
        if (list.includes("0") && list.length === 1) {
          checkboxes[0].checked = true;
        } else {
          checkboxes.forEach((box) => {
            if (list.includes(box.value)) {
              box.checked = true;
            }
          });
        }
      }
    }
  }
  document
    .querySelector(".modal__form")
    .addEventListener("submit", (e) =>
      updateAppointment(e, fields_value["id"])
    );
}

// update appointment details in database when revise form submitted
function updateAppointment(e, id) {
  e.preventDefault();
  const form = new FormData(e.target);
  const add_ons = e.target.querySelectorAll("input[type=checkbox]");
  let add_ons_list = [];
  add_ons.forEach((box) =>
    box.checked === true ? add_ons_list.push(box.value) : false
  );

  fetch(`/appointment/${id}`, {
    method: "PUT",
    body: JSON.stringify({
      dog: form.get("dog"),
      date: form.get("date"),
      time: form.get("time"),
      service: form.get("service"),
      add_ons: add_ons_list,
    }),
    headers: { "X-CSRFToken": csrftoken },
  })
    .then((response) => {
      if (response.ok) {
        modalDisplay("msgDiv");
        document.querySelector(".modal__msg").innerHTML =
          "<p>Updated Successfully</p>";
        setTimeout(() => modalDisplay(), 2000);
      } else {
        return response.json();
      }
    })
    .then((result) => {
      if (result.error) {
        modalDisplay("msgDiv");
        const msgDiv = document.querySelector(".modal__msg");
        msgDiv.innerHTML = `<p>${result.error}</p>`;
        setTimeout(() => msgDiv.remove(), 2000);
      }
    });
}

// delete appointment record when user cancels a booking
function cancelBooking(id) {
  modalDisplay("msgDiv");
  const msgDiv = document.querySelector(".modal__msg");
  msgDiv.innerHTML =
    '<p>Are you sure?<p><div class="btn-group flex"><button class="btn btn-inverted" id="confirm">confirm</button><button class="btn" id="no">No</button></div>';
  document
    .getElementById("no")
    .addEventListener("click", () => modalDisplay("text"));
  document.getElementById("confirm").addEventListener("click", () => {
    const msgDiv = document.querySelector(".modal__msg");

    // del booking record in system
    fetch(`/appointment/${id}`, {
      method: "DELETE",
      body: JSON.stringify({
        id: id,
      }),
      headers: { "X-CSRFToken": csrftoken },
    })
      .then((response) => {
        if (response.ok) {
          msgDiv.innerHTML = "<p>Deleted successfully<p>";
          setTimeout(() => modalDisplay(), 1500);
        } else {
          return response.json();
        }
      })
      .then((result) => {
        if (result.error) {
          msgDiv.innerHTML = `<p>${result.error}<p>`;
        }
      });
  });
}

// take care of what to display inside the modal
function modalDisplay(element = "none") {
  const form = document.querySelector(".modal__form");
  const text = document.querySelector(".modal__text");
  const msgDiv = document.querySelector(".modal__msg");
  const modal = document.querySelector(".modal");
  msgDiv && msgDiv.remove();

  if (element === "form") {
    document.querySelector(".modal__form").style.display = "block";
    document.querySelector(".modal__text").style.display = "none";
  } else if (element === "text") {
    document.querySelector(".modal__form").style.display = "none";
    form.reset();
    document.querySelector(".modal__text").style.display = "flex";
  } else if (element === "msgDiv") {
    const msgDiv = document.createElement("div");
    msgDiv.classList.add("modal__msg", "center");
    document.querySelector(".modal__content").append(msgDiv);
  } else {
    modal.classList.remove("show-modal");
    setTimeout(() => location.reload(), 1500);
  }
}
