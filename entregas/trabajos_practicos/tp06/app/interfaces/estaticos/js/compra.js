const cantidadInput = document.querySelector("#cantidad");
const edadesContainer = document.querySelector("#edades-visitantes");
const fechaInput = document.querySelector("#fecha-visita");
const mensajeFecha = document.querySelector("#mensaje-fecha");
const formulario = document.querySelector(".formulario");
const formaPagoSelect = document.querySelector("#forma-pago");
const modalMercadoPago = document.querySelector("#modal-mercadopago");
const pasoQr = document.querySelector("#paso-qr");
const pasoSpinner = document.querySelector("#paso-spinner");
const canvasQr = document.querySelector("#qr-mercadopago");

let pagoMercadoPagoListo = false;

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
        input.addEventListener("input", () => {
            const edad = Number.parseInt(input.value, 10);

            if (edad < 0) {
                input.value = "0";
            } else if (edad > 120) {
                input.value = "120";
            }
        });

        label.appendChild(input);
        edadesContainer.appendChild(label);
    }
}

function dibujarPatronFinder(ctx, origenX, origenY, celda) {
    ctx.fillStyle = "#000000";
    ctx.fillRect(origenX * celda, origenY * celda, 7 * celda, 7 * celda);
    ctx.fillStyle = "#ffffff";
    ctx.fillRect((origenX + 1) * celda, (origenY + 1) * celda, 5 * celda, 5 * celda);
    ctx.fillStyle = "#000000";
    ctx.fillRect((origenX + 2) * celda, (origenY + 2) * celda, 3 * celda, 3 * celda);
}

function generarQrAleatorio(canvas) {
    const modulos = 21;
    const celda = Math.floor(canvas.width / modulos);
    const ctx = canvas.getContext("2d");
    const semilla = `${Date.now()}-${Math.random().toString(36).slice(2)}`;

    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    for (let fila = 0; fila < modulos; fila += 1) {
        for (let columna = 0; columna < modulos; columna += 1) {
            const enFinder =
                (fila < 8 && columna < 8) ||
                (fila < 8 && columna > modulos - 9) ||
                (fila > modulos - 9 && columna < 8);

            if (enFinder) {
                continue;
            }

            const hash = (semilla.charCodeAt((fila * modulos + columna) % semilla.length) +
                fila * 17 +
                columna * 31) %
                2;

            if (hash === 0) {
                ctx.fillStyle = "#000000";
                ctx.fillRect(columna * celda, fila * celda, celda, celda);
            }
        }
    }

    dibujarPatronFinder(ctx, 0, 0, celda);
    dibujarPatronFinder(ctx, modulos - 7, 0, celda);
    dibujarPatronFinder(ctx, 0, modulos - 7, celda);
}

function mostrarPaso(paso) {
    pasoQr.hidden = paso !== "qr";
    pasoSpinner.hidden = paso !== "spinner";
}

function esperar(ms) {
    return new Promise((resolver) => {
        setTimeout(resolver, ms);
    });
}

async function iniciarPagoMercadoPago() {
    generarQrAleatorio(canvasQr);
    mostrarPaso("qr");
    modalMercadoPago.showModal();

    await esperar(5000);
    mostrarPaso("spinner");
    await esperar(3000);

    pagoMercadoPagoListo = true;
    modalMercadoPago.close();
    formulario.requestSubmit();
}

cantidadInput.addEventListener("input", () => {
    const cantidad = Number.parseInt(cantidadInput.value, 10);

    if (cantidad > 10) {
        cantidadInput.value = "10";
    } else if (cantidad < 1 && cantidadInput.value !== "") {
        cantidadInput.value = "1";
    }

    actualizarCamposDeEdad();
});
fechaInput.addEventListener("input", validarFechaSeleccionada);
fechaInput.addEventListener("change", validarFechaSeleccionada);
formulario.addEventListener("submit", (evento) => {
    validarFechaSeleccionada();

    if (!fechaInput.value) {
        evento.preventDefault();
        return;
    }

    if (formaPagoSelect.value === "mercadopago" && !pagoMercadoPagoListo) {
        evento.preventDefault();
        iniciarPagoMercadoPago();
    }
});
validarFechaSeleccionada();
