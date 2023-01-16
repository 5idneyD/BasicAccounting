const Table = (props) => {
	const rows = [];

	for (let i = 0; i <= Number(props.rows); i++) {
		rows.push(i);
	}

	return (
		<table>
			<thead>
				<tr>
					<th>Row</th>
					<th>Nominal Code</th>
					<th>Description</th>
					<th>Debit</th>
					<th>Credit</th>
				</tr>
			</thead>
			<tbody>
				{rows.map((row) => {
					return (
						<tr>
							<td>{row}</td>
							<td>{row}</td>
							<td>{row}</td>
							<td>{row}</td>
							<td>{row}</td>
						</tr>
					);
				})}
			</tbody>
		</table>
	);
};

const root = document.querySelector("#data");
ReactDOM.render(<Table rows="5" />, root);
