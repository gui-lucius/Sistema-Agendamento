import { mostrarMensagemGlobal } from "./utils.js";

export let selectedDate = "";
export const modal = document.getElementById("reservaModal");

export function abrirModal(startStr) {
  if (startStr) selectedDate = startStr;
  modal.style.display = "flex";
  modal.classList.add("ativo");
  mostrarProximoStep(1);
  document.getElementById("nome").focus();
}

export function fecharModal() {
  modal.style.display = "none";
  modal.classList.remove("ativo");
}

export function mostrarProximoStep(n) {
  for (let i = 1; i <= 3; i++) {
    const el = document.getElementById(`step-${i}`);
    if (el) el.style.display = (i === n) ? "block" : "none";
  }
}

window.mostrarProximoStep = mostrarProximoStep;
