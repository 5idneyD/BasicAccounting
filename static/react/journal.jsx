function Rows() {
	const [rows, addRow] = React.useState(1);

	return (
		<>
			<button onClick={() => addRow(rows+1)}>Add Row</button>
            <Table rows={rows}/>
		</>
	);
    }



const Table = (props) => {
	const rows = [];

	for (let i = 1; i <= Number(props.rows); i++) {
		rows.push(i);
	}

	return (
		<>
			<table>
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
							<tr>
								<td>{row}</td>
								<td><input type="invoice"></input></td>
								<td><input type="invoice"></input></td>
                                <td><input type="invoice"></input></td>
                                <td><input type="invoice"></input></td>
							</tr>
						);
					})}
				</tbody>
			</table>
		</>
	);
};

const root = document.querySelector("#data");
ReactDOM.render(<Rows />, root);
