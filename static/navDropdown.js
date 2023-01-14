document.addEventListener(
    "click",
    function (e) {
        var menu = document.querySelector("#" + e.target.id);
        var url = window.location.pathname;
        url = url.substring(0, url.lastIndexOf("/"));


        if (menu.dataset.expanded == "false") {
            menu.parentElement.style.height = "14vh";
            if (menu.id == "salesLedger") {
                menu.insertAdjacentHTML(
                    "beforeend",
                    "<br class=" +
                    e.target.id +
                    "Option><a class='menuOption " +
                    e.target.id +
                    "Option'>Add Sales Invoice</a><br class=" +
                    e.target.id +
                    "Option><a class='menuOption " +
                    e.target.id +
                    "Option' href='" + url + "/Customers'>View Customers</a>",
                );
                menu.dataset.expanded = "true";
            } else if (menu.id == "purchaseLedger") {
                menu.insertAdjacentHTML(
                    "beforeend",
                    "<br class=" +
                    e.target.id +
                    "Option><a class='menuOption " +
                    e.target.id +
                    "Option'>Add Purchase Invoice</a><br class=" +
                    e.target.id +
                    "Option><a class='menuOption " +
                    e.target.id +
                    "Option'>View Suppliers</a>",
                );
                menu.dataset.expanded = "true";
            } else {
                menu.insertAdjacentHTML(
                    "beforeend",
                    "<br class=" +
                    e.target.id +
                    "Option><a class='menuOption " +
                    e.target.id +
                    "Option'>Trial Balance</a><br class=" +
                    e.target.id +
                    "Option><a class='menuOption " +
                    e.target.id +
                    "Option' href='" + url + "/chartOfAccounts'>Chart Of Accounts</a>",
                );
                menu.dataset.expanded = "true";
            }
        } else {
            var options = document.querySelectorAll("." + e.target.id + "Option");
            options.forEach((option) => {
                option.remove();
                menu.dataset.expanded = "false";
                menu.parentElement.style.height = "8vh";
            });
        }
    },
    false,
);