const cantidadInput = document.querySelector("#cantidad");
const edadesContainer = document.querySelector("#edades-visitantes");
const fechaInput = document.querySelector("#fecha-visita");
const mensajeFecha = document.querySelector("#mensaje-fecha");
const formulario = document.querySelector(".formulario");
const formaPagoSelect = document.querySelector("#forma-pago");
const modalMercadoPago = document.querySelector("#modal-mercadopago");
const pasoRedireccion = document.querySelector("#paso-redireccion");
const pasoSpinner = document.querySelector("#paso-spinner");
const botonCancelarPago = document.querySelector("#boton-cancelar-pago");

const URL_PAGO_MERCADOPAGO = "/mercadopago-simulado";

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

function mostrarPaso(paso) {
    pasoRedireccion.hidden = paso !== "redireccion";
    pasoSpinner.hidden = paso !== "spinner";
}

function esperar(ms) {
    return new Promise((resolver) => {
        setTimeout(resolver, ms);
    });
}

async function iniciarPagoMercadoPago() {
    localStorage.removeItem("pago_mp");
    mostrarPaso("redireccion");
    modalMercadoPago.showModal();

    await esperar(800);
    window.open(URL_PAGO_MERCADOPAGO, "_blank");
    mostrarPaso("spinner");
}

window.addEventListener("storage", (evento) => {
    if (evento.key !== "pago_mp" || evento.newValue !== "ok") {
        return;
    }
    localStorage.removeItem("pago_mp");
    pagoMercadoPagoListo = true;
    modalMercadoPago.close();
    formulario.requestSubmit();
});

if (botonCancelarPago) {
    botonCancelarPago.addEventListener("click", () => modalMercadoPago.close());
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
formulario.addEventListener("submit", async (evento) => {
    validarFechaSeleccionada();

    // Si la fecha no es válida, frenamos todo
    if (!fechaInput.value) {
        evento.preventDefault();
        return;
    }

    if (formaPagoSelect.value === "mercadopago" && !pagoMercadoPagoListo) {
        evento.preventDefault(); 

        const formData = new FormData(formulario);
        try {
            const respuesta = await fetch('/compras/validar', {
                method: 'POST',
                body: formData
            });

            if (respuesta.ok) {
                const datosCompra = {};
                for (const [clave, valor] of formData.entries()) {
                    if (!datosCompra[clave]) {
                        datosCompra[clave] = [];
                    }
                    datosCompra[clave].push(valor);
                }

                sessionStorage.setItem("compra_pendiente", JSON.stringify(datosCompra));

                iniciarPagoMercadoPago();
            } else {
                
                const datosError = await respuesta.json();
                const msjError = document.querySelector("#mensaje-error");
                if (msjError) {
                    msjError.textContent = datosError.error;
                    msjError.hidden = false;
                }
            }
        } catch (error) {
            console.error("Error al validar la compra:", error);
        }
    }
});

document.querySelector("#boton-cancelar-pago").addEventListener("click", () => modalMercadoPago.close());