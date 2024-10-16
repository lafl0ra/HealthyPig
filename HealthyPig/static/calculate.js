console.log("calculate.js has been loaded");

function calculate() {
    console.log("calculate function called");
    const amountField = document.querySelector('[name="amount"]');
    const amount = parseFloat(amountField.value);
    const cal = parseFloat('{{ food.calories }}');
    console.log("Amount:", amount);
    console.log("Calories per gram:", cal);
    if (isNaN(amount) || isNaN(cal)) {
        alert("Please enter a valid amount.");
        return;
    }
    const result = (amount * cal).toFixed(2) + " kcal";
    console.log("Result:", result);
    document.getElementById('resultInput').value = result;
}
