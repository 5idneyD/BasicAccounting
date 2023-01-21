var references = document.querySelector("#references").dataset.references;
var company = document.querySelector("#references").dataset.company;
var invoice_number_element = document.querySelector("#invoice_number");
var submitButton = document.querySelector("#submitButton");

var new_number = Number(references[references.length - 3]) + 1;
invoice_number_element.value = new_number;

invoice_number_element.addEventListener("change", function () {
    var new_reference = company + invoice_number_element.value;
    if (references.includes(new_reference)) {
        invoice_number_element.style.border = "1px solid red";
        // submitButton.setAttribute("disabled", "disabled")
        document.querySelector("#submitButton").type = "button";
    } else {

        invoice_number_element.style.border = "1px solid gray";
        document.querySelector("#submitButton").type = "submit";
        document.querySelector("#submitButton").classList.remove("error")
    }
});



document.addEventListener("click", function (e) {
    console.log(e.target.id)
    if (document.querySelector("#submitButton").type == "button" && e.target.id=="submitButton"){
    var el = document.querySelector("#invoice_number");
    el.classList.toggle("error");
    }
}
);