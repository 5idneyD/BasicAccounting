var addUserButton = document.querySelector("#addUserButton");
var removeUserButton = document.querySelector("#removeUserButton");
var chartOfAccountsButton = document.querySelector("#chartOfAccountsButton");
var closePeriodButton = document.querySelector("#closePeriodButton");
var invoiceDetailsButton = document.querySelector("#invoiceDetailsButton")

// removeUserButton.style.backgroundColor = "rgba(20, 20, 20, 0.4)";
// chartOfAccountsButton.style.backgroundColor = "rgba(20, 20, 20, 0.4)";
// closePeriodButton.style.backgroundColor = "rgba(20, 20, 20, 0.4)";
// invoiceDetailsButton.style.backgroundColor = "rgba(20, 20, 20, 0.4)";

function clicked(buttonId) {
    var adminButtons = document.querySelectorAll(".adminButton");
    adminButtons.forEach(element => {
        if (element.id == buttonId) {
            element.dataset.selected = "1"
        } else {
            element.dataset.selected = "0";
        }
    //     if (element.id == buttonId) {
    //         element.style.backgroundColor = "#3D5B59";
    //         element.style.color = "#B5E5CF";
    //     } else {
    //         element.style.backgroundColor = "rgba(20, 20, 20, 0.4)";
    //         element.style.color = "#151f1e";
    //     }
     });
}