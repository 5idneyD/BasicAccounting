var addUserButton=document.querySelector("#addUserButton"),removeUserButton=document.querySelector("#removeUserButton"),chartOfAccountsButton=document.querySelector("#chartOfAccountsButton"),closePeriodButton=document.querySelector("#closePeriodButton"),invoiceDetailsButton=document.querySelector("#invoiceDetailsButton");function clicked(e){var o=document.querySelectorAll(".adminButton");o.forEach(t=>{t.id==e?t.dataset.selected="1":t.dataset.selected="0"})}
