var els = document.querySelectorAll(".table_row");
var revenueTotalP = 0;
var directCostsTotalP = 0;
var overheadsTotalP = 0;
var revenueTotalM = 0;
var directCostsTotalM = 0;
var overheadsTotalM = 0;
els.forEach(function (el) {
    if (el.classList[0][0] == "1") {
        revenueTotalP += Number(el.children[1].innerText);
        revenueTotalM += Number(el.children[2].innerText);
    } else if (el.classList[0][0] == "2") {
        directCostsTotalP += Number(el.children[1].innerText);
        directCostsTotalM += Number(el.children[2].innerText)
    } else if (el.classList[0][0] == "3") {
        overheadsTotalP += Number(el.children[1].innerText)
        overheadsTotalM += Number(el.children[2].innerText)
    }
});

els.forEach(function (el, index) {
    if (els[index].classList[0][0] == "1" && els[index + 1].classList[0][0] == "2") {
        el.insertAdjacentHTML(
            "afterend",
            "<tr class='summaryRow'><td>Total Revenue</td><td>" + revenueTotalP + "</td><td>" + revenueTotalM + "</td></tr>",
        );
    } else if (els[index].classList[0][0] == "2" && els[index + 1].classList[0][0] == "3"){
        el.insertAdjacentHTML(
            "afterend",
            "<tr class='summaryRow'><td>Gross Profit</td><td>" + (revenueTotalP - directCostsTotalP) + "</td><td>" + (revenueTotalM - directCostsTotalM) + "</td></tr>",
        );
    } else if (els[index].classList[0][0] == "3" && !els[index + 1]){
        el.insertAdjacentHTML(
            "afterend",
            "<tr class='summaryRow'><td>Net Profit</td><td>" + (revenueTotalP - directCostsTotalP - overheadsTotalP) + "</td><td>" + (revenueTotalM - directCostsTotalM - overheadsTotalM) + "</td></tr>",
        );
    }
});