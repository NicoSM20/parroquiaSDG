let fueExito = false;
let campoOrigen = null;
let modalPersona = null;
let modalMensaje = null;

document.addEventListener('DOMContentLoaded', function() {
    modalPersona = new bootstrap.Modal(document.getElementById('modalPersona'));
    modalMensaje = new bootstrap.Modal(document.getElementById('mensajeModal'));
    
    // Configurar eventos para campos DNI
    configurarCamposDNI();
    
    // Configurar formulario principal
    configurarFormularioPrincipal();
});

function configurarCamposDNI() {
    const camposDNI = document.querySelectorAll('.dni-input');
    
    camposDNI.forEach(campo => {
        // Solo permitir números
        campo.addEventListener('input', function(e) {
            this.value = this.value.replace(/[^0-9]/g, '');
        });
        
        // Buscar persona al presionar Enter
        campo.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                if (this.value.length === 8) {
                    buscarPersona(this.value, this.id);
                } else {
                    alert('El DNI debe tener 8 dígitos');
                }
            }
        });
    });
}

async function buscarPersona(dni, campoId) {
    try {
        const response = await fetch('/buscar_persona', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ dni: dni })
        });
        
        const data = await response.json();
        
        if (data.encontrado) {
            // Mostrar datos de la persona
            mostrarDatosPersona(data.persona, campoId);
        } else {
            // Abrir modal para registrar nueva persona
            abrirModalPersona(dni, campoId);
        }
    } catch (error) {
        console.error('Error al buscar persona:', error);
        alert('Error al buscar la persona. Intente nuevamente.');
    }
}

function mostrarDatosPersona(persona, campoId) {
    const tipo = campoId.replace('dni', '').toLowerCase();
    
    // Mapear campos según el tipo
    const prefijos = {
        'persona': 'Persona',
        'padre': 'Padre',
        'madre': 'Madre',
        'padrino': 'Padrino',
        'madrina': 'Madrina'
    };
    
    const prefijo = prefijos[tipo] || 'Persona';
    
    // Llenar campos
    document.getElementById(`nombres${prefijo}`).value = persona.nombres;
    document.getElementById(`apellido1${prefijo}`).value = persona.apellido1;
    document.getElementById(`apellido2${prefijo}`).value = persona.apellido2 || '';
    
    // Mostrar contenedor de datos
    document.getElementById(`datos${prefijo}`).classList.remove('d-none');
    
    // Mensaje de confirmación
    showToast(`Datos de ${persona.nombres} ${persona.apellido1} cargados correctamente`, 'success');
}

function abrirModalPersona(dni, campoId) {
    campoOrigen = campoId;
    document.getElementById('dniNuevo').value = dni;
    modalPersona.show();
}

async function guardarPersona() {
    const formData = {
        dni: document.getElementById('dniNuevo').value,
        nombres: document.getElementById('nombres').value,
        apellido1: document.getElementById('apellido1').value,
        apellido2: document.getElementById('apellido2').value,
        genero: document.getElementById('genero').value
    };
    
    // Validar campos requeridos
    if (!formData.dni || !formData.nombres || !formData.apellido1 || !formData.genero) {
        alert('Por favor complete todos los campos requeridos');
        return;
    }
    
    try {
        const response = await fetch('/registrar_persona', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (data.exito) {
            // Cerrar modal
            modalPersona.hide();
            
            // Mostrar datos en el formulario
            mostrarDatosPersona(formData, campoOrigen);
            
            // Limpiar formulario del modal
            document.getElementById('formPersona').reset();
            
            showToast('Persona registrada exitosamente', 'success');
        } else {
            alert(data.mensaje || 'Error al registrar la persona');
        }
    } catch (error) {
        console.error('Error al registrar persona:', error);
        alert('Error al registrar la persona. Intente nuevamente.');
    }
}

function configurarFormularioPrincipal() {
    document.getElementById('formBautizo').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Validar que se haya ingresado al menos el DNI del bautizado
        if (!document.getElementById('dniPersona').value) {
            alert('Debe ingresar el DNI del bautizado');
            return;
        }
        
        // Recopilar datos del formulario
        const formData = {
            dni_bautizado: document.getElementById('dniPersona').value,
            dni_padre: document.getElementById('dniPadre').value || null,
            dni_madre: document.getElementById('dniMadre').value || null,
            dni_padrino: document.getElementById('dniPadrino').value || null,
            dni_madrina: document.getElementById('dniMadrina').value || null,
            partida: document.getElementById('partida').value,
            fecha_bautizo: document.getElementById('fechaBautizo').value,
            iglesia: document.getElementById('iglesia').value,
            ano_parroquial: document.getElementById('anoParroquial').value,
            sacerdote: document.getElementById('sacerdote').value
        };
        
        try {
            const response = await fetch('/registrar_bautizo', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify(formData)
            });
            
            const data = await response.json();
            
            // Mostrar mensaje en modal
            document.getElementById('mensajeContenido').textContent = data.mensaje;
            fueExito = !data.mensaje.includes('❌');
            modalMensaje.show();
            
            if (fueExito) {
                // Limpiar formulario
                document.getElementById('formBautizo').reset();
                // Ocultar todos los contenedores de datos
                document.querySelectorAll('[id^="datos"]').forEach(el => {
                    el.classList.add('d-none');
                });
            }
        } catch (error) {
            console.error('Error al registrar bautizo:', error);
            alert('Error al registrar el bautizo. Intente nuevamente.');
        }
    });
}

function cerrarModal() {
    modalMensaje.hide();
    if (fueExito) {
        // Opcional: redirigir o hacer alguna acción adicional
        showToast('Bautizo registrado exitosamente', 'success');
    }
}

function showToast(mensaje, tipo = 'info') {
    // Crear toast dinámicamente
    const toastContainer = document.getElementById('toastContainer') || createToastContainer();
    
    const toastEl = document.createElement('div');
    toastEl.className = `toast align-items-center text-white bg-${tipo === 'success' ? 'success' : 'primary'} border-0`;
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');
    
    toastEl.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${mensaje}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toastEl);
    
    const toast = new bootstrap.Toast(toastEl);
    toast.show();
    
    // Eliminar toast después de que se oculte
    toastEl.addEventListener('hidden.bs.toast', function() {
        toastEl.remove();
    });
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    return container;
}