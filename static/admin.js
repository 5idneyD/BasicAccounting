var div = document.querySelector("#body");
buttons = document.querySelectorAll(".adminButton");

function changeForm() {
    buttons.forEach(element => {
        if (element.dataset.selected == 1) {
            var option = element.id.toString().slice(0, element.id.toString().length - "Button".length);
            console.log(option);
            if (option == "addUser") {
                div.innerHTML = addUser;
            } else if (option == "removeUser") {
                div.innerHTML = removeUser;
            } else {
                div.innerHTML = chartOfAccounts;
            }
        } 
    })
}

var addUser = `
<div class="d-flex flex-grow-1 justify-content-center align-items-center">
        <div class="container w-50">
            <div class="row">
                <div class="col">
                    <input type="name" name="name" placeholder="name" aria-required="true"/>
                </div>
            </div>
            <div class="row">
                <div class="col">
                    <input type="email" name="email" placeholder="email" aria-required="true"/>
                </div>
            </div>
            <div class="row">
                <div class="col">
                    <input type="password" name="password" placeholder="password" aria-required="true"/>
                </div>
            </div>
            <div class="row">
                <div class="col mt-5">
                    <button type="submit" name="signinButton">Add User</button>
                </div>
            </div>
        </div>
`;

var removeUser =
    `
<div class="d-flex flex-grow-1 justify-content-center align-items-center">
        <div class="container w-50">
            <div class="row">
                <div class="col">
                    <input type="email" name="email" placeholder="user's email" aria-required="true"/>
                </div>
            </div>
            <div class="row">
                <div class="col">
                    <input type="password" name="password" placeholder="admin password" aria-required="true"/>
                </div>
            </div>
            <div class="row">
                <div class="col mt-5">
                    <button type="submit" name="signinButton">Remove User</button>
                </div>
            </div>
        </div>
`;
var chartOfAccounts =
    `
<div class="d-flex flex-grow-1 justify-content-center align-items-center">
        <div class="container w-50">
            <div class="row">
                <div class="col">
                    <input type="name" name="nominal" placeholder="Nominal Code" aria-required="true"/>
                </div>
            </div>
            <div class="row">
                <div class="col">
                    <input type="name" name="accountName" placeholder="Account Name" aria-required="true"/>
                </div>
            </div>
            <div class="row">
                <div class="col mt-5">
                    <button type="submit" name="signinButton">Add Nominal Account</button>
                </div>
            </div>
        </div>
`;


