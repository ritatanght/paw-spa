//toggle add pet form
const add_btn = document.querySelector(".add-pet");
add_btn.addEventListener("click", togglePetForm);

function togglePetForm() {
  document.querySelector(".pet-form").classList.toggle("show-form");
}

// form will be populate according to the slot clicked
document.querySelectorAll(".free").forEach((slot) => {
  slot.addEventListener("click", pickSlot);
});

function pickSlot(e) {
  const slot = e.target.id.split("_");
  document
    .querySelectorAll(".free")
    .forEach((slot) => slot.classList.remove("selected"));
  e.target.classList.add("selected");
  let pickedDate = slot[0];
  let pickedTime = slot[1];
  // date field
  document.getElementById("id_date").value = pickedDate;

  // time field
  const timeField = document
    .getElementById("id_time")
    .querySelectorAll("option");
  timeField.forEach((option) => {
    if (option.value === pickedTime) {
      option.selected = true;
    }
  });
}

// prev and next arrow to load schedule
document
  .querySelector(".week-prev")
  .addEventListener("click", () => loadSlotPreview("prev"));
document
  .querySelector(".week-next")
  .addEventListener("click", () => loadSlotPreview("next"));

function loadSlotPreview(move) {
  // this enable us to get the first date in the preview table
  let start = document.querySelector(".date__text").id;

  fetch(`/schedule/${start}/${move}`)
    .then((response) => response.json())
    .then((result) => {
      if (result.message) {
        alert(result.message);
      } else {
        const slot_dict = result.slot_dict;
        const date_list = document.querySelector(".preview__date-list");
        let html = "";
        const months = [
          "Jan",
          "Feb",
          "Mar",
          "Apr",
          "Mau",
          "Jun",
          "Jul",
          "Aug",
          "Sep",
          "Oct",
          "Nov",
          "Dec",
        ];
        for (let key in result.slot_dict) {
          const date = key.split("-");
          const [year, month, day, dayWeek] = date;

          const monthString = months[parseInt(month) - 1];

          html =
            html +
            ` 
                    <div class="date__col center">
                        <p class="date__text" id="${year}-${month}-${day}">${parseInt(
              day
            )} ${monthString} (${dayWeek})</p>
                        <div class="time">`;
          const slot_list = result.slot_dict[key];
          if (slot_list === "Closed") {
            html += '<p class="closed">Closed</p>';
          } else {
            for (let i = 0, len = slot_list.length; i < len; i++) {
              if (slot_list[i] == 10) {
                html += `<p class="free" id="${year}-${month}-${day}_${slot_list[i]}">10:00 AM</p>`;
              } else if (slot_list[i] == 13) {
                html += `<p class="free" id="${year}-${month}-${day}_${slot_list[i]}">1:00 PM</p>`;
              } else if (slot_list[i] == 15) {
                html += `<p class="free" id="${year}-${month}-${day}_${slot_list[i]}">3:00 PM</p>`;
              } else {
                html += '<p class="na">Not Avaliable</p>';
              }
            }
          }

          html = html + "</div></div>";
        }
        date_list.innerHTML = html;
        document.querySelectorAll(".free").forEach((slot) => {
          slot.addEventListener("click", pickSlot);
        });
        // consider whether to display the preview arrows
        let start = document.querySelector(".date__text").id;
        const today = new Date().toLocaleDateString("en-CA", {
          year: "numeric",
          month: "2-digit",
          day: "2-digit",
        });
        let fiveWeeks = new Date();
        fiveWeeks.setDate(fiveWeeks.getDate() + 28);
        fiveWeeks = fiveWeeks.toLocaleDateString("en-CA", {
          year: "numeric",
          month: "2-digit",
          day: "2-digit",
        });
        if (start === today) {
          document
            .querySelector(".week-prev")
            .classList.add("preview-disabled");
        } else if (start === fiveWeeks) {
          document
            .querySelector(".week-next")
            .classList.add("preview-disabled");
        } else {
          document
            .querySelector(".week-prev")
            .classList.remove("preview-disabled");
          document
            .querySelector(".week-next")
            .classList.remove("preview-disabled");
        }
      }
    });
}

// add-ons checkboxes behaviour - none box cannot be checked when other boxes are checked
const checkbox = document.querySelectorAll("input[type=checkbox]");

checkbox.forEach((box) => {
  box.addEventListener("change", (e) => {
    // when the None box is checked
    if (e.target.checked && e.target.value === "0") {
      checkbox.forEach((checkedbox) => {
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
