window.onload=function(){var s=document.querySelectorAll(".table_row"),e=0,r=0;s.forEach(function(t){t.classList[0][0]=="6"?(e+=Number(t.children[2].innerText),e-=Number(t.children[3].innerText)):t.classList[0][0]=="7"&&(r+=Number(t.children[2].innerText),r-=Number(t.children[3].innerText))}),s.forEach(function(t,d){console.log(s[d].classList[0][0]),s[d].classList[0][0]=="6"&&s[d+1].classList[0][0]=="7"?e>=0?t.insertAdjacentHTML("afterend","<tr class='summaryRow'><td></td><td>Total Assets</td><td>"+e+"</td><td></td></tr>"):t.insertAdjacentHTML("afterend","<tr class='summaryRow'><td></td><td>Total Assets</td><td></td><td>"+e*-1+"</td></tr>"):s[d].classList[0][0]=="7"&&!s[d+1]&&(r>=0?t.insertAdjacentHTML("afterend","<tr class='summaryRow'><td></td><td>Total Liabilities</td><td>"+r+"</td><td></td></tr>"):t.insertAdjacentHTML("afterend","<tr class='summaryRow'><td></td><td>Total Liabilities</td><td></td><td>"+r*-1+"</td></tr>"))});var i=document.querySelector("#netAssets"),a=e+r;a<0?i.children[3].innerText=-a:i.children[2].innerText=a};
