function HeadTable() {
	return (
		<>
			<table className="col-3" id="journalHead">
				<tbody>
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
				</tbody>
			</table>
			<button type="submit">Post Journal</button>
		</>
	);
}

ReactDOM.render(<HeadTable />, document.querySelector("#headTable"));

const Table = (props) => {
	const rows = [];

	for (let i = 1; i <= Number(props.rows); i++) {
		rows.push(i);
	}

	return (
		<>
			<input name="number_of_rows" value={props.rows}></input>
			<table id="journalBody">
				<thead>
					<tr>
						<th>Row</th>
						<th>Nominal Code</th>
						<th className="invoiceHeaderDescription">Description</th>
						<th>Debit</th>
						<th>Credit</th>
					</tr>
				</thead>
				<tbody>
					{rows.map((row) => {
						return (
							<tr key={row}>
								<td>{row}</td>
								<td>
									<input type="invoice" name={row + "_nominal_code"}></input>
								</td>
								<td>
									<input type="invoice" name={row + "_description"}></input>
								</td>
								<td>
									<input type="invoice" name={row + "_debit"}></input>
								</td>
								<td>
									<input type="invoice" name={row + "_credit"}></input>
								</td>
							</tr>
						);
					})}
				</tbody>
			</table>
		</>
	);
};

function Rows() {
	const [rows, addRow] = React.useState(1);

	return (
		<>
			<Table rows={rows} />
			<button type="button" onClick={() => addRow(rows + 1)}>
				Add Row
			</button>
		</>
	);
}

const root = document.querySelector("#mainTable");
ReactDOM.render(<Rows />, root);
