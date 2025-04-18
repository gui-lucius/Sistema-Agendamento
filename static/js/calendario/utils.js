export function isoFromString(dataStr) {
    return new Date(dataStr).toISOString();
  }
  
  export function mostrarMensagemGlobal(texto, tipo = "erro") {
    const msg = document.getElementById("mensagem-global");
    msg.textContent = texto;
    msg.className = tipo;
    msg.style.display = "block";
    setTimeout(() => {
      msg.style.display = "none";
    }, 4000);
  }
  