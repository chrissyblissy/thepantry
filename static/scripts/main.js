const extraInput = "<div class='form-row'><div class='col mb-2'><input type='text' class='form-control' placeholder='Ingredient' name='ingredient' required></div><div class='col mb-3'><input type='text' class='form-control' placeholder='Amount' name='amount'></div></div>"

$(document).ready(() => {

    $("#appendbtn").on("click", () => {
        $("#appendingredients").append(extraInput);
    })

    $("#removebtn").on("click", () => {
        $("#appendingredients .form-row:last").remove();
    })

})