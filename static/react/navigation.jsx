function App() {
	return (
		<ul>
			<li id="salesLedgerMenu" class="menuHead">
				<a id="salesLedger" data-expanded="false">
					Sales Ledger
				</a>
				<br />
			</li>
			<li id="purchaseLedgerMenu" class="menuHead">
				<a id="purchaseLedger" data-expanded="false">
					Purchase Ledger
				</a>
				<br />
			</li>
			<li id="financialsMenu" class="menuHead">
				<a id="financials" data-expanded="false">
					Financials
				</a>
				<br />
			</li>
			<li id="otherMenu" class="menuHead">
				<a id="other" data-expanded="false">
					Other
				</a>
				<br />
			</li>
		</ul>
	);
}

ReactDOM.render(<App />, document.querySelector("#nav"));
