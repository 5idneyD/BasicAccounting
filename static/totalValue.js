function calculateTotals() {
    var i = 0;
    var els = document.querySelectorAll(".tv");
    els.forEach(e => {
        i += 1;
        var total = document.querySelector('input[name="' + i + '_total_value"]');
        var net = document.querySelector('input[name="' + i + '_net_value"]');
        var vat = document.querySelector('input[name="' + i + '_vat"]');
        total.value = Number(net.value) + Number(vat.value);
    })
}

function addVAT() {
    var vatSetting = document.querySelector("#vatSetting");

    if (vatSetting.value == "yes") {
        var i = 0
        var vatCells = document.querySelectorAll(".vat");

        vatCells.forEach(cell => {
            i += 1;
            var net = document.querySelector('input[name="' + i + '_net_value"]');

            var vat = document.querySelector('input[name="' + i + '_vat"]');
            if (net.value) {
                console.log(net.value);
                vat.value = (parseFloat(net.value) * 0.2).toFixed(2);
            };
        })
    }
}

function calculate(){
var nets = document.querySelectorAll(".net");

nets.forEach(net => {
    net.addEventListener(
        "change", function(){
            addVAT();
            calculateTotals();
        }
    )
})
}

calculate();