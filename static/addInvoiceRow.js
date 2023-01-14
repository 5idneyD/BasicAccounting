function addInvoiceRow() {
    var table = document.querySelector("#bodyTable");

    var html = `
        <tr>
            <td><input type="text"></td>
            <td><input type="text"></td>
            <td><input type="text"></td>
            <td><input type="text"></td>
            <td><input type="text"></td>
        </tr>
 `

    table.insertAdjacentHTML("beforeend", html);
};