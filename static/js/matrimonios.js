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




["dniEsposo", "dniEsposa"].forEach((idCampoDni) => {
  const input = document.getElementById(idCampoDni);
  const ruta = idCampoDni === "dniEsposo" ? "/buscar_persona_esposo" : "/buscar_persona_esposa";

  input.addEventListener("keydown", async function (e) {
    if (e.key === "Enter") {
      e.preventDefault();
      const dni = this.value.trim();
      console.log(dni);
      if (dni.length !== 8) {
        alert("⚠️ DNI debe tener 8 dígitos");
        return;
      }

      try {
        const res = await fetch(ruta, {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({ dni })
        });

        const data = await res.json();
        const base = idCampoDni.replace("dni", "");
        console.log(base);
        console.log(data);

        if (data.existe) {
          document.getElementById("nombre" + base).value = data.nombre;
          document.getElementById("id" + base).value = data.id;

          // Padre/Madre si vienen
          if (data.nombre_padre)
            document.getElementById("nombrePadre" + base).value = data.nombre_padre;
          if (data.nombre_madre)
            document.getElementById("nombreMadre" + base).value = data.nombre_madre;

          // Estado civil si lo quieres autoseleccionar
          document.getElementById("estadocivil" + base).value = data.estado_civil;

        } else {
          abrirModal(idCampoDni);  // Aquí puedes abrir modal para registrar persona
        }

      } catch (err) {
        console.error("Error al buscar persona:", err);
        alert("Error al buscar persona.");
      }
    }
  });

  // Limpiar campos si se cambia el DNI a menos de 8
  input.addEventListener("input", function () {
    const base = idCampoDni.replace("dni", "");
    if (this.value.trim().length < 8) {
      const campos = ["nombre", "id", "nombrePadre", "nombreMadre"];
      campos.forEach(c => {
        const el = document.getElementById(c + base);
        if (el) el.value = "";
      });
    }
  });
});