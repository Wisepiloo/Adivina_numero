// genera un numero del 0 al 9
function generar_numero_random(){
    const max = 10;
    return Math.floor(Math.random() * max);
}

// muestra el numero
function cambiar_numero_html(numero){
    const html_numero = document.querySelector(".numero_random");
    html_numero.textContent = numero;
}

// comprobar si el btn presionado es igual al numero
function comprobar_respuesta_btn(respuesta_btn){
    const numero_random = generar_numero_random();
    cambiar_numero_html(numero_random);
    return numero_random == respuesta_btn.textContent;
}

// suma 100 por cada acierto
function sumar_puntaje() {
    let cantidad = parseInt(puntaje.textContent, 10);
    puntaje.textContent = cantidad + 100;
}

// inicializar las variables
let incorrectas = 0;
let correctas = 0;

// obtener los botones y otros elementos del DOM
const btns = document.querySelectorAll(".respuesta_btn");
const contenedor = document.querySelector(".numero_random");
const puntaje = document.querySelector(".puntaje");

btns.forEach((btn) => {
    btn.addEventListener('click', () => {
        if (comprobar_respuesta_btn(btn)) {
            contenedor.style.backgroundColor = "rgb(2, 97, 2)";
            sumar_puntaje();
            correctas += 1; // incrementa correctas
        } else {
            contenedor.style.backgroundColor = "rgb(85, 4, 4)";
            incorrectas += 1; // incrementa incorrectas
        }

        // restaurar el color después de un breve tiempo
        setTimeout(() => {
            contenedor.style.backgroundColor = "#000";
        }, 300);
        let datos = {
            correctas: correctas,
            incorrectas: incorrectas,
            puntaje: parseInt(puntaje.textContent, 10)
        };
        enviar_datos(datos);
    });
});

// Función para enviar datos con fetch
function enviar_datos(datos) {
    
    fetch('/guardar_datos', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(datos) // Asegúrate de convertir el objeto a JSON
    })
};

