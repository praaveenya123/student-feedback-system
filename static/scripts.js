let wasSubmitted = false;

function checkBeforeSubmit() {
  let radios = document.querySelectorAll('input[type="radio"]:checked');
  if (radios.length === 0) {
    alert("Please select an answer before submitting!");
    return false;
  }
  if (wasSubmitted) {
    alert("Form already submitted!");
    return false;
  }
  wasSubmitted = true;
  return true;
}
