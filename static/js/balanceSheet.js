var els = document.querySelectorAll(".table_row");
			var assetsTotal = 0;
			var liabilitiesTotal = 0;

			els.forEach(function (el) {
				if (el.classList[0][0] == "6") {
					assetsTotal += Number(el.children[2].innerText);
					assetsTotal -= Number(el.children[3].innerText);
				} else if (el.classList[0][0] == "7") {
					liabilitiesTotal += Number(el.children[2].innerText);
					liabilitiesTotal -= Number(el.children[3].innerText);
				}
			});

			els.forEach(function (el, index) {
				if (els[index].classList[0][0] == "6" && els[index + 1].classList[0][0] == "7") {
					if (assetsTotal >= 0) {
						el.insertAdjacentHTML(
							"afterend",
							"<tr class='summaryRow'><td></td><td>Total Assets</td><td>" +
								assetsTotal +
								"</td><td></td></tr>",
						);
					} else {
						el.insertAdjacentHTML(
							"afterend",
							"<tr class='summaryRow'><td></td><td>Total Assets</td><td></td><td>" +
								assetsTotal * -1 +
								"</td></tr>",
						);
					}
				} else if (els[index].classList[0][0] == "7" && !els[index + 1]) {
					if (liabilitiesTotal >= 0) {
						el.insertAdjacentHTML(
							"afterend",
							"<tr class='summaryRow'><td></td><td>Total Liabilities</td><td>" +
								liabilitiesTotal +
								"</td><td></td></tr>",
						);
					} else {
						el.insertAdjacentHTML(
							"afterend",
							"<tr class='summaryRow'><td></td><td>Total Liabilities</td><td></td><td>" +
								liabilitiesTotal * -1 +
								"</td></tr>",
						);
					}
				}
			});


			var netAssetsRow = document.querySelector("#netAssets");
			var netAssets = assetsTotal + liabilitiesTotal;
			if (netAssets < 0){
			netAssetsRow.children[3].innerText = -netAssets;
			} else {
			netAssetsRow.children[2].innerText = netAssets;	
			}