var els=document.querySelectorAll(".table_row");let revenueTotalP=0,directCostsTotalP=0,overheadsTotalP=0,revenueTotalM=0,directCostsTotalM=0,overheadsTotalM=0,revenueBudgetTotalP=0,directCostsBudgetTotalP=0,overheadsBudgetTotalP=0,revenueBudgetTotalM=0,directCostsBudgetTotalM=0,overheadsBudgetTotalM=0;els.forEach(function(t){t.classList[0][0]=="1"?(revenueTotalP+=Number(t.children[1].innerText),revenueTotalM+=Number(t.children[2].innerText),revenueBudgetTotalP+=Number(t.children[4].innerText),revenueBudgetTotalM+=Number(t.children[5].innerText)):t.classList[0][0]=="2"?(directCostsTotalP+=Number(t.children[1].innerText),directCostsTotalM+=Number(t.children[2].innerText),directCostsBudgetTotalP+=Number(t.children[4].innerText),directCostsBudgetTotalM+=Number(t.children[5].innerText)):t.classList[0][0]=="3"&&(overheadsTotalP+=Number(t.children[1].innerText),overheadsTotalM+=Number(t.children[2].innerText),overheadsBudgetTotalP+=Number(t.children[4].innerText),overheadsBudgetTotalM+=Number(t.children[5].innerText))}),els.forEach(function(t,e){els[e].classList[0][0]=="1"&&els[e+1].classList[0][0]!="1"&&t.insertAdjacentHTML("afterend","<tr class='summaryRow'><td>Total Revenue</td><td>"+revenueTotalP+"</td><td>"+revenueTotalM+"</td><td>"+(revenueTotalP-revenueTotalM)+"</td><td>"+revenueBudgetTotalP+"</td><td>"+revenueBudgetTotalM+"</td><td>"+(revenueBudgetTotalP-revenueBudgetTotalM)+"</td></tr>"),els[e+1]||t.insertAdjacentHTML("afterend","<tr class='summaryRow'><td>Net Profit</td><td>"+(revenueTotalP-directCostsTotalP-overheadsTotalP)+"</td><td>"+(revenueTotalM-directCostsTotalM-overheadsTotalM)+"</td><td>"+(revenueTotalP-directCostsTotalP-overheadsTotalP-(revenueTotalM-directCostsTotalM-overheadsTotalM))+"</td><td>"+(revenueBudgetTotalP-directCostsBudgetTotalP-overheadsBudgetTotalP)+"</td><td>"+(revenueBudgetTotalM-directCostsBudgetTotalM-overheadsBudgetTotalM)+"</td><td>"+(revenueBudgetTotalP-directCostsBudgetTotalP-overheadsBudgetTotalP-(revenueBudgetTotalM-directCostsBudgetTotalM-overheadsBudgetTotalM))+"</td></tr>"),els[e].classList[0][0]=="2"&&els[e+1].classList[0][0]=="3"&&t.insertAdjacentHTML("afterend","<tr class='summaryRow'><td>Gross Profit</td><td>"+(revenueTotalP-directCostsTotalP)+"</td><td>"+(revenueTotalM-directCostsTotalM)+"</td><td>"+(revenueTotalP-directCostsTotalP-(revenueTotalM-directCostsTotalM))+"</td><td>"+(revenueBudgetTotalP-directCostsBudgetTotalP)+"</td><td>"+(revenueBudgetTotalM-directCostsBudgetTotalM)+"</td><td>"+(revenueBudgetTotalP-directCostsBudgetTotalP-(revenueBudgetTotalM-directCostsBudgetTotalM))+"</td></tr>")});for(var els=document.getElementById("table").getElementsByTagName("td"),i=1;i<els.length;i++)Number(els[i].innerText).toLocaleString("en")=="NaN"||(els[i].innerText=Number(els[i].innerText).toLocaleString("en"));
