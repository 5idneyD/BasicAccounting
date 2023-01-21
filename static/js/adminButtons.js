var addUserButton = document.querySelector("#addUserButton");
var removeUserButton = document.querySelector("#removeUserButton");
var chartOfAccountsButton = document.querySelector("#chartOfAccountsButton");

removeUserButton.style.backgroundColor = "rgba(20, 20, 20, 0.4)";
chartOfAccountsButton.style.backgroundColor = "rgba(20, 20, 20, 0.4)";

function clicked(buttonId) {
    var adminButtons = document.querySelectorAll(".adminButton");
    adminButtons.forEach(element => {
        if (element.id == buttonId) {
            element.dataset.selected = 1
        } else {
            element.dataset.selected = 0;
        }
        if (element.dataset.selected == 1) {
            element.style.backgroundColor = "#A15C38";
            element.style.color = "#F7F1F0";
        } else {
            element.style.backgroundColor = "rgba(20, 20, 20, 0.4)";
            element.style.color = "#151f1e";
        }
    });
}