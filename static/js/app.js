document.addEventListener('DOMContentLoaded', () => {
    console.log("DOM completamente cargado y parseado.");

    const btnAtender = document.getElementById('btnAtender');
    const btnGestionar = document.getElementById('btnGestionar');
    const btnConsultar = document.getElementById('btnConsultar');

    const backFromEmergencias = document.getElementById('backFromEmergencias');
    const backFromGestionar = document.getElementById('backFromGestionar');
    const backFromHistorial = document.getElementById('backFromHistorial');

    const mainScreen = document.getElementById('mainScreen');
    const screenEmergencias = document.getElementById('screenEmergencias');
    const screenGestionar = document.getElementById('screenGestionar');
    const screenHistorial = document.getElementById('screenHistorial');

    const ubicacionInput = document.getElementById('ubicacion');
    const unidadInput = document.getElementById('unidad');
    const ubicacionesDatalist = document.getElementById('ubicaciones-opciones');
    const unidadesDatalist = document.getElementById('unidades-opciones');
    const btnCalcularRuta = document.getElementById('btnCalcularRuta');
    const btnAudioRadio = document.getElementById('btnAudioRadio');

    const elementoHora = document.getElementById('hora-actual');

    function actualizarHora() {
        const ahora = new Date();
        // toLocaleTimeString formatea la hora al formato local (ej: 12:27:20 PM)
        // 'es-PE' es para el formato de Perú.
        elementoHora.textContent = ahora.toLocaleTimeString('es-PE', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    }

    actualizarHora();

    // Configura un intervalo para que la función se ejecute cada segundo
    setInterval(actualizarHora, 1000);

    function showScreen(screenToShow) {
        if (!screenToShow) {
            console.error("Error: Intentando mostrar una pantalla nula.");
            return;
        }
        console.log(`Cambiando a pantalla: ${screenToShow.id}`);

        document.querySelectorAll('.screen').forEach(screen => {
            screen.classList.remove('active-screen');
        });

        screenToShow.classList.add('active-screen');

    }

    if (btnAtender) {
        btnAtender.addEventListener('click', () => {
            console.log("Clic en 'Atender Emergencias' detectado.");
            showScreen(screenEmergencias);
            setTimeout(() => {
                if (window.map) {
                    window.map.invalidateSize();
                }
            }, 200); // Espera breve para asegurar que el DOM se haya actualizado
        });
    } else {
        console.error("ERROR: Botón 'Atender Emergencias' (id='btnAtender') no encontrado. Verifica el HTML.");
    }
    if (btnGestionar) {
        btnGestionar.addEventListener('click', () => {
            console.log("Clic en 'Gestionar Unidades' detectado.");
            showScreen(screenGestionar);
        });
    } else {
        console.warn("ADVERTENCIA: Botón 'Gestionar Unidades' (id='btnGestionar') no encontrado.");
    }

    if (btnConsultar) {
        btnConsultar.addEventListener('click', () => {
            console.log("Clic en 'Consultar Historial' detectado.");
            showScreen(screenHistorial);
        });
    } else {
        console.warn("ADVERTENCIA: Botón 'Consultar Historial' (id='btnConsultar') no encontrado.");
    }


    if (backFromEmergencias) {
        backFromEmergencias.addEventListener('click', () => {
            console.log("Clic en 'Volver' desde Emergencias detectado.");
            showScreen(mainScreen);

        });
    } else {
        console.warn("ADVERTENCIA: Botón 'Volver' de Emergencias (id='backFromEmergencias') no encontrado.");
    }

    if (backFromGestionar) {
        backFromGestionar.addEventListener('click', () => {
            console.log("Clic en 'Volver' desde Gestionar detectado.");
            showScreen(mainScreen);
        });
    } else {
        console.warn("ADVERTENCIA: Botón 'Volver' de Gestionar (id='backFromGestionar') no encontrado.");
    }

    if (backFromHistorial) {
        backFromHistorial.addEventListener('click', () => {
            console.log("Clic en 'Volver' desde Historial detectado.");
            showScreen(mainScreen);
        });
    } else {
        console.warn("ADVERTENCIA: Botón 'Volver' de Historial (id='backFromHistorial') no encontrado.");
    }

    const ubicacionesData = [
        "Jirón de la Unión 825, Lima",
        "Avenida Arequipa 123, Lince",
        "Plaza Mayor de Lima, Cercado de Lima",
        "Avenida Javier Prado Este 5000, La Molina",
        "Centro Cívico de Lima, Cercado de Lima",
        "Mercado Central, Cercado de Lima"
    ];

    const unidadesData = [
        "Unidad N-11 San Borja-Claudio Galeno 200",
        "Unidad N-28 Miraflores-Av. Andrés Avelino Cáceres 172",
        "Unidad N-8 La Victoria-Jr. Manuel Cisneros 597",
        "Unidad N-2 Suquillo-",
        "Unidad N-100 San Isidro-C. Godofredo García 439,",

        { nombre: "Unidad N-11 San Borja-Claudio Galeno 200", lat: -12.106924903119632, lng: -77.00736715413291 },
        { nombre: "Unidad N-28 Miraflores-Av. Andrés Avelino Cáceres 172", lat: -12.119742044236054, lng: -77.02273735483284 },
        { nombre: "Unidad N-8 La Victoria-Jr. Manuel Cisneros 597", lat: -12.067531374600396, lng: -77.02116186429399 },
        { nombre: "Unidad N-2 Suquillo-", lat: -12.106924903119632, lng: -77.00736715413291 },
        { nombre: "Unidad N-100 San Isidro-C. Godofredo García 439,", lat: -12.10653801709604, lng: -77.05435961047738 },


    ];
    if (unidadesDatalist) {
        populateDatalist(unidadesDatalist, unidadesData.map(u => u.nombre));
    } else {
        console.error("ERROR: Datalist 'unidades-opciones' no encontrado. Verifica el HTML.");
    }
    if (unidadInput) {
        unidadInput.addEventListener('change', function () {
            const seleccion = unidadInput.value;
            const unidad = unidadesData.find(u => u.nombre === seleccion);
            if (unidad && window.map) {
                // Si ya existe un marcador de unidad, elimínalo
                if (window.unidadMarker) {
                    window.map.removeLayer(window.unidadMarker);
                }
                // Crea un nuevo marcador y guárdalo en window.unidadMarker
                window.unidadMarker = L.marker([unidad.lat, unidad.lng]).addTo(window.map);
                window.map.setView([unidad.lat, unidad.lng], 16); // Centra el mapa
                console.log(`Unidad seleccionada: ${unidad.nombre} en (${unidad.lat}, ${unidad.lng})`);
            }
        });
    } else {
        console.warn("ADVERTENCIA: Input de unidad (id='unidad') no encontrado.");
    }
    function populateDatalist(datalistElement, dataArray) {
        if (!datalistElement) {
            return;
        }
        datalistElement.innerHTML = '';
        dataArray.forEach(item => {
            const option = document.createElement('option');
            option.value = item;
            datalistElement.appendChild(option);
        });
        console.log(`Datalist '${datalistElement.id}' poblado con ${dataArray.length} ítems.`);
    }

    if (ubicacionesDatalist) {
        populateDatalist(ubicacionesDatalist, ubicacionesData);
    } else {
        console.error("ERROR: Datalist 'ubicaciones-opciones' no encontrado. Verifica el HTML.");
    }

    if (unidadesDatalist) {
        populateDatalist(unidadesDatalist, unidadesData);
    } else {
        console.error("ERROR: Datalist 'unidades-opciones' no encontrado. Verifica el HTML.");
    }


    document.querySelectorAll('.input-action-btn').forEach(button => {
        button.addEventListener('click', (event) => {
            const input = event.currentTarget.previousElementSibling;
            if (event.currentTarget.classList.contains('clear-btn')) {
                input.value = '';
                console.log(`Campo '${input.id}' limpiado.`);
            } else {
                console.log(`Acción de buscar en campo '${input.id}' con valor: '${input.value}'`);
            }
        });
    });


    if (btnCalcularRuta) {
        btnCalcularRuta.addEventListener('click', () => {
            const ubicacion = ubicacionInput ? ubicacionInput.value : 'N/A';
            const unidad = unidadInput ? unidadInput.value : 'N/A';
            console.log(`Clic en 'CALCULAR RUTA ÓPTIMA' para: ${ubicacion} con ${unidad}`);

            // Simular resultados
            const tiempoEstimadoElem = document.getElementById('tiempoEstimado');
            const distanciaElem = document.getElementById('distancia');
            const instruccionesElem = document.getElementById('instrucciones');

            if (tiempoEstimadoElem) tiempoEstimadoElem.textContent = '00:15:30'; else console.warn("Elemento 'tiempoEstimado' no encontrado.");
            if (distanciaElem) distanciaElem.textContent = '5.2 km'; else console.warn("Elemento 'distancia' no encontrado.");
            if (instruccionesElem) instruccionesElem.value = "1. Salir de la base y girar a la derecha.\n2. Conducir 2km por la Av. Principal.\n3. Girar a la izquierda en Calle AAA.\n4. Llegada a destino."; else console.warn("Elemento 'instrucciones' no encontrado.");

            console.log("Resultados de ruta simulados actualizados.");
        });
    } else {
        console.warn("ADVERTENCIA: Botón 'CALCULAR RUTA ÓPTIMA' (id='btnCalcularRuta') no encontrado.");
    }

    if (btnAudioRadio) {
        btnAudioRadio.addEventListener('click', () => {
            const instrucciones = document.getElementById('instrucciones');
            if (instrucciones && 'speechSynthesis' in window) {
                const utterance = new SpeechSynthesisUtterance(instrucciones.value);
                utterance.lang = 'es-ES';
                speechSynthesis.speak(utterance);
                console.log('Reproduciendo instrucciones de audio...');
            } else {
                alert('Tu navegador no soporta la síntesis de voz o el campo de instrucciones no existe.');
                console.warn('SpeechSynthesis API no soportada o campo de instrucciones no encontrado.');
            }
        });
    } else {
        console.warn("ADVERTENCIA: Botón 'AUDIO/RADIO' (id='btnAudioRadio') no encontrado.");
    }

});