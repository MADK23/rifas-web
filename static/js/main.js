let seleccionados = [];

const numeros = document.querySelectorAll(".numero");
const textoSeleccionados = document.getElementById("seleccionados");

numeros.forEach(numero => {

    if(numero.classList.contains("disponible")){

        numero.addEventListener("click", () => {

            const valor = numero.dataset.numero;

            if(seleccionados.includes(valor)){

                seleccionados =
                    seleccionados.filter(n => n !== valor);

                numero.classList.remove("seleccionado");

            }else{

                seleccionados.push(valor);

                numero.classList.add("seleccionado");

            }

            actualizarTexto();

        });

    }


    function actualizarTexto(){

    if(seleccionados.length === 0){

        textoSeleccionados.textContent =
            "Ninguno";

        return;

    }

    textoSeleccionados.textContent =
        seleccionados.join(", ");

}


const botonContinuar =
    document.getElementById("continuar");

botonContinuar.addEventListener("click", ()=>{

    if(seleccionados.length === 0){

        alert("Selecciona al menos un número");

        return;

    }

    const numeros =
        seleccionados.join(",");

    window.location.href =
        "/compra?numeros=" + numeros;

        window.location.href =
    "/compra?numeros=" + numerosSeleccionados.join(",");

});

});

