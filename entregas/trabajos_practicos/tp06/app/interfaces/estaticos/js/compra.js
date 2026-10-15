const cantidadInput = document.querySelector("#cantidad");
const edadesContainer = document.querySelector("#edades-visitantes");

function actualizarCamposDeEdad() {
    const cantidad = Number.parseInt(cantidadInput.value, 10) || 0;
    const edadesActuales = Array.from(
        edadesContainer.querySelectorAll("input[name='edades']")
    ).map((input) => input.value);

    edadesContainer.replaceChildren();

    for (let indice = 0; indice < cantidad; indice += 1) {
        const label = document.createElement("label");
        const input = document.createElement("input");

        label.className = "campo";
        label.htmlFor = `edad-${indice + 1}`;
        label.textContent = `Edad del visitante ${indice + 1}`;

        input.id = `edad-${indice + 1}`;
        input.name = "edades";
        input.type = "number";
        input.min = "0";
        input.max = "120";
        input.required = true;
        input.value = edadesActuales[indice] || "";

        label.appendChild(input);
        edadesContainer.appendChild(label);
    }
}

cantidadInput.addEventListener("input", actualizarCamposDeEdad);
