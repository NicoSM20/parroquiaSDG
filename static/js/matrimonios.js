let campoOrigen = null;

function abrirModal(origen) {
  campoOrigen = origen;
  document.getElementById("modalPersona").style.display = "block";
  document.getElementById("dniNuevo").value = document.getElementById(origen).value;
}

function cerrarModal() {
  document.getElementById("modalPersona").style.display = "none";
  document.getElementById("modalPersona").querySelectorAll("input, select").forEach(el => el.value = '');
}

async function guardarPersona() {
  const payload = {
    dni: document.getElementById("dniNuevo").value,
    nombres: document.getElementById("nombres").value,
    apellido1: document.getElementById("apellido1").value,
    apellido2: document.getElementById("apellido2").value,
    genero: document.getElementById("genero").value
  };

  const res = await fetch("/registrar_persona", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  const data = await res.json();

  if (data.mensaje) {
    alert(data.mensaje);
    const campo = document.getElementById(campoOrigen);
    campo.value = payload.dni;

    cerrarModal();

    const enterEvent = new KeyboardEvent("keydown", {
      key: "Enter",
      bubbles: true,
      cancelable: true
    });
    campo.dispatchEvent(enterEvent);
  } else {
    alert(data.error || "❌ No se pudo registrar");
  }
}

// Buscar persona en BD al presionar Enter en campos de DNI
document.querySelectorAll('input.dni-input').forEach(input => {
  input.addEventListener('keydown', async function (e) {
    if (e.key === 'Enter') {
      e.preventDefault();
      const dni = this.value.trim();
      const campo = this.id;

      if (dni.length !== 8) {
        alert("⚠️ DNI debe tener 8 dígitos");
        return;
      }

      const res = await fetch("/buscar_persona_por_dni", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ dni })
      });

      const data = await res.json();

      const nombreCampo = campo.replace("dni", "nombre");
      const idCampo = campo.replace("dni", "id");

      if (data.existe) {
        // ✅ Mostrar el nombre completo en el input deshabilitado
        document.getElementById(nombreCampo).value = data.nombre;
        document.getElementById(idCampo).value = data.id;
      } else {
        abrirModal(campo);
      }
    }
  });

  input.addEventListener('input', function () {
    const campo = this.id;
    const nombreCampo = campo.replace("dni", "nombre");
    const idCampo = campo.replace("dni", "id");

    if (this.value.trim().length < 8) {
      const inputNombre = document.getElementById(nombreCampo);
      const inputId = document.getElementById(idCampo);
      if (inputNombre) inputNombre.value = "";
      if (inputId) inputId.value = "";
    }
  });
});
