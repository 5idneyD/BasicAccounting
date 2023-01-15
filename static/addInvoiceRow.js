var row_number = 2
var table = document.querySelector("#bodyTable");
var number_of_rows_input = document.querySelector("#number_of_rows");
number_of_rows_input.value = 1;

function addInvoiceRow() {

    var html = `
        <tr class="invoiceRow">
            <td>` + row_number + `
            <td><input type="text" name='` + row_number + `_nominal_code'></td>
            <td><input type="text" name='` + row_number + `_description'></td>
            <td><input type="text" name='` + row_number + `_net_value' class='net'></td>
            <td><input type="text" name='` + row_number + `_vat' class='vat'></td>
            <td><input type="text" name='` + row_number + `_total_value' class='tv'></td>
        </tr>
 `
    row_number += 1;
    table.insertAdjacentHTML("beforeend", html);
    table.dataset.rows = row_number - 1;
    number_of_rows_input.value = table.dataset.rows;
};