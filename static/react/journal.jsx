var references = document.querySelector("#references").dataset.references;
var new_number = Number(references);


function Journal() {
	const [debit, setDebit] = React.useState(0);
	const [credit, setCredit] = React.useState(0);
	const [count, setCount] = React.useState(1);
	const [rows, setRows] = React.useState([<Row key="1" number="1" />]);
	const [journalNumber, setJournalNumber] = React.useState(new_number);


	function Row(props) {
		return (
			<tr>
				<td>{props.number}</td>
				<td>
					<input type="invoice" name={props.number + "_nominal_code"}></input>
				</td>
				<td>
					<input type="invoice" name={props.number + "_description"}></input>
				</td>
				<td>
					<input
						type="invoice"
						className="debit"
						name={props.number + "_debit"}
						onChange={() => sumDebits()}></input>
				</td>
				<td>
					<input
						type="invoice"
						className="credit"
						name={props.number + "_credit"}
						onChange={() => sumCredits()}></input>
				</td>
			</tr>
		);
	}

	function addRow() {
		setCount(count + 1);
		const a = count + 1;
		setRows(rows.concat(<Row key={a} number={a} />));
	}

	function sumDebits() {
		var debits = document.querySelectorAll(".debit");
		var debitTotal = 0;
		debits.forEach((debit) => {
			debitTotal += Number(debit.value);
		});
		setDebit(debitTotal);
	}

	function sumCredits() {
		var credits = document.querySelectorAll(".credit");
		var creditTotal = 0;
		credits.forEach((credit) => {
			creditTotal += Number(credit.value);
		});
		setCredit(creditTotal);
	}

	function checkBalancing() {
		if (debit - credit != 0) {
			document.querySelector("#submitButton").type = "button";
		} else {
			try {
				document.querySelector("#submitButton").type = "submit";
			} catch {}
		}
	}

	return (
		<>
			<div className="col-4">
				{/* Table Head */}
				<table className="" id="journalHead">
					<tbody>
						<tr>
							<td>Journal Number</td>
							<td>
								<input type="journal" name="journalNumber" defaultValue={journalNumber} readOnly></input>
							</td>
						</tr>
						<tr>
							<td>Date</td>
							<td>
								<input type="date" name="journalDate"></input>
							</td>
						</tr>
						<tr>
							<td>Description</td>
							<td>
								<input type="journal" name="journalDescription" />
							</td>
						</tr>
						<tr>
							<td>Debit Total</td>
							<td>{debit}</td>
						</tr>
						<tr>
							<td>Credit Total</td>
							<td>{credit}</td>
						</tr>
					</tbody>
				</table>

				{/* buttons */}
				<button type="button" onClick={() => addRow()}>
					Add Row
				</button>
				<br></br>
				<button type="submit" id="submitButton">
					Post Journal
				</button>
			</div>
			<div className="col">
				{/* Table Body */}
				<table className="col">
					<thead>
						<tr>
							<th>Row</th>
							<th>Nominal</th>
							<th>Description</th>
							<th>Debit</th>
							<th>Credit</th>
						</tr>
					</thead>
					<tbody id="bodyTable">{rows}</tbody>
				</table>
				<input name="number_of_rows" value={count}></input>
				<input name="debitTotal" value={debit} onChange={checkBalancing()}></input>
				<input name="creditTotal" value={credit} onChange={checkBalancing()}></input>
			</div>
		</>
	);
}

ReactDOM.render(<Journal />, document.querySelector("#headTable"));
