$(document).ready(function () {
    console.log("hi")
    var items = [];

    $("#saveServiceBtn").on("click", addItemToList);
    $("#table").on("click", "#delete_button", removeItemFromList);

    function update_total_cost() {
        var total_cost = 0;
        items.forEach(function (item) {
            total_cost += item.total_price * item.hours;
        });

        $("#total_cost").text(total_cost);
    }
    function addItemToList(event) {
        event.preventDefault();

        var service_name = $("#modal_input-service_name").val();
        var hours = $("#modal_input-hours").val();
        var price_per_hour = $("#modal_input-price_per_hour").val();

        if (service_name !== "" && price_per_hour !== "" && hours !== "") {
            var item = {
                name: service_name,
                price_per_hour: price_per_hour,
                hours: hours,
            }

            var total_price = hours * price_per_hour;

            items.push(item);
            $("#table tbody").append(`
                <tr>
                <td><input class="hidden" name="service_name[]" value="${service_name}">${service_name}</td>
                <td><input class="hidden" name="hours[]" value="${hours}">${hours}</td>
                <td><input class="hidden" name="price_per_hour[]" value="${price_per_hour}">£${price_per_hour}</td>
                <td><input class="hidden" name="total_price[]" value="${total_price}">£${total_price}</td>
                <td>
                    <button type="button"  class="btn btn-outline-error btn-xs" id="delete_button">
                    <i class="fa-solid fa-trash-can pe-2"></i> Delete
                    </button>
                </td>
                </tr>
            `);


            console.log("Submitted" + service_name + hours + price_per_hour);
        } else {
            console.log("Invalid Input");
        }

    }

    function removeItemFromList() {
        var index = $(this).closest("tr").index();
        items.slice(index, 1);
        $(this).closest("tr").remove();
        update_total_cost();
    }
})