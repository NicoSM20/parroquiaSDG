function toggleRecibo() {
  const checkbox = document.getElementById("registrarRecibo");
  const reciboSection = document.getElementById("reciboSection");
  reciboSection.style.display = checkbox.checked ? "block" : "none";
}

function obtenerHora24() {
  const hora = parseInt(document.getElementById("hora_12").value);
  const ampm = document.getElementById("ampm").value;

  if (isNaN(hora) || !ampm) return null;

  let hora24 = hora;

  if (ampm === "AM") {
    if (hora === 12) hora24 = 0;
  } else if (ampm === "PM") {
    if (hora !== 12) hora24 = hora + 12;
  }

  return `${hora24.toString().padStart(2, "0")}:00`;
}

function validarDominical() {
  const tipoMisa = document.getElementById("idtipomisas");
  const selectedText =
    tipoMisa.options[tipoMisa.selectedIndex].text.toLowerCase();
  const esDominical = selectedText.includes("dominical");

  const container = document.getElementById("hora_misa_container");

  if (esDominical) {
    container.innerHTML = `
      <div id="hora_misa_dominical" class="space-y-2">
        <label for="hora_12" class="block text-sm font-medium text-gray-700 mb-1">Hora</label>
        <select id="hora_12"
          class="w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-2 focus:ring-blue-500"
          onchange="sincronizarHoraMisa()" required>
          <option value="">Seleccione hora</option>
          <option value="07:00-AM">07:00 AM</option>
          <option value="10:00-AM">10:00 AM</option>
          <option value="07:00-PM">07:00 PM</option>
        </select>
        <input type="hidden" id="hora_misa" name="hora_misa">
      </div>
    `;
  } else {
    container.innerHTML = `
  
    <div class="col-span-1">
      <label for="hora_12" class="block text-sm font-medium text-gray-700 mb-1">Hora</label>
      <select id="hora_12"
        class="w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-2 focus:ring-blue-500"
        onchange="sincronizarHoraMisa()" required>
        ${[...Array(12).keys()]
          .map((i) => {
            const val = (i + 1).toString().padStart(2, "0");
            return `<option value="${val}">${val}</option>`;
          })
          .join("")}
      </select>
    </div>

    <div class="col-span-1 hidden">
      <label class="block text-sm font-medium text-gray-700 mb-1">Minutos</label>
      <select id="minutos_12"
        class="w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-2 focus:ring-blue-500"
        disabled>
        <option value="00">00</option>
      </select>
    </div>

    <div class="col-span-1">
      <label for="ampm" class="block text-sm font-medium text-gray-700 mb-1">AM/PM</label>
      <select id="ampm"
        class="w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-2 focus:ring-blue-500"
        onchange="sincronizarHoraMisa()" required>
        <option value="">Seleccione</option>
        <option value="AM">AM</option>
        <option value="PM">PM</option>
      </select>
    </div>
  
  <input type="hidden" id="hora_misa" name="hora_misa">
`;
  }
}

function sincronizarHoraMisa() {
  const hiddenInput = document.getElementById("hora_misa");

  const hora12 = document.getElementById("hora_12");
  const ampm = document.getElementById("ampm");

  // Si estamos en el modo restringido
  if (!ampm) {
    const valor = hora12.value;
    if (valor) {
      const [hora, periodo] = valor.split("-");
      let hora24 = parseInt(hora);
      if (periodo === "AM") {
        if (hora24 === 12) hora24 = 0;
      } else {
        if (hora24 !== 12) hora24 += 12;
      }
      hiddenInput.value = hora24.toString().padStart(2, "0") + ":00";
    } else {
      hiddenInput.value = "";
    }
  } else {
    // Modo libre
    const hora = parseInt(hora12.value);
    const periodo = ampm.value;

    if (!isNaN(hora) && periodo) {
      let hora24 = hora;
      if (periodo === "AM") {
        if (hora === 12) hora24 = 0;
      } else {
        if (hora !== 12) hora24 += 12;
      }
      hiddenInput.value = hora24.toString().padStart(2, "0") + ":00";
    } else {
      hiddenInput.value = "";
    }
  }
  console.log("Hora: ", hiddenInput.value);
}
function cerrarModal() {
  if (fueExito) {
    // Redirigir, recargar o mostrar otra cosa
    window.location.href = "/misas_por_fecha"; // Cambia esto según tu lógica
    // o simplemente actualizar parte de la interfaz
    // location.reload();  // Si deseas recargar
  } else {
    const modal = bootstrap.Modal.getInstance(
      document.getElementById("mensajeModal")
    );
    modal.hide(); // Solo cerrar el modal
  }
}

let fueExito = false; // Guarda si fue exitoso o no
toggleRecibo();
document.getElementById("reciboSection").classList.toggle("hidden");

document.querySelector("form").addEventListener("submit", async function (e) {
  e.preventDefault();

  const form = e.target;
  const formData = new FormData(form);
  try {
    const response = await fetch(form.action, {
      method: "POST",
      headers: {
        "X-Requested-With": "XMLHttpRequest",
      },
      body: formData,
    });

    const data = await response.json();

    const mensajeContenido = document.getElementById("mensajeContenido");
    mensajeContenido.textContent = data.mensaje || "No se recibió mensaje.";

    // Detectamos si fue exitoso o no
    fueExito = !data.mensaje.includes("❌");

    const modal = new bootstrap.Modal(document.getElementById("mensajeModal"));
    modal.show();

    if (fueExito) {
      form.reset();
      toggleRecibo();
    }
  } catch (error) {
    alert("Ocurrió un error al registrar: " + error.message);
    fueExito = false;
  }
});
