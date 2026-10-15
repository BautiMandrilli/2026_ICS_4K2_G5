const cantidadInput = document.querySelector("#cantidad");
const edadesContainer = document.querySelector("#edades-visitantes");
const fechaInput = document.querySelector("#fecha-visita");
const mensajeFecha = document.querySelector("#mensaje-fecha");
const formulario = document.querySelector(".formulario");

function esFechaCerrada(fechaTexto) {
    const [anio, mes, dia] = fechaTexto.split("-").map(Number);
    const fecha = new Date(anio, mes - 1, dia);
    const esLunes = fecha.getDay() === 1;
    const esFeriado = (mes === 1 && dia === 1) || (mes === 12 && dia === 25);

    return esLunes || esFeriado;
}

if (typeof flatpickr === "function") {
    flatpickr(fechaInput, {
        locale: flatpickr.l10ns.es,
        disableMobile: true,
        minDate: "today",
        dateFormat: "Y-m-d",
        disable: [
            (fecha) => fecha.getDay() === 1,
            (fecha) => {
                const mes = fecha.getMonth() + 1;
                const dia = fecha.getDate();
                return (mes === 1 && dia === 1) || (mes === 12 && dia === 25);
            },
        ],
    });
}

function validarFechaSeleccionada() {
    if (!fechaInput.value || !esFechaCerrada(fechaInput.value)) {
        mensajeFecha.hidden = true;
        mensajeFecha.textContent = "";
        return;
    }

    mensajeFecha.hidden = false;
    mensajeFecha.textContent = "El parque esta cerrado los lunes y los dias 1 de enero y 25 de diciembre.";
    fechaInput.value = "";
}

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
fechaInput.addEventListener("input", validarFechaSeleccionada);
fechaInput.addEventListener("change", validarFechaSeleccionada);
formulario.addEventListener("submit", (evento) => {
    validarFechaSeleccionada();

    if (!fechaInput.value) {
        evento.preventDefault();
    }
});
validarFechaSeleccionada();
