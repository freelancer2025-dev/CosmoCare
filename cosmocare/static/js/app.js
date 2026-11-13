document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll('input[type="number"]').forEach((input) => {
    input.addEventListener("change", () => {
      const min = Number(input.min || 1), max = Number(input.max || 999);
      let value = Number(input.value || min);
      input.value = Math.max(min, Math.min(max, value));
    });
  });
});
