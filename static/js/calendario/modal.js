import { mostrarMensagemGlobal } from "./utils.js";

export let selectedDate = "";
export const modal = document.getElementById("reservaModal");

// 👉 Abre o modal e mostra o primeiro passo
export function abrirModal(startStr) {
  if (startStr) selectedDate = startStr;
  modal.style.display = "flex";
  modal.classList.add("ativo");
  mostrarProximoStep(1);
  document.getElementById("nome").focus();
}

// 👉 Fecha o modal
export function fecharModal() {
  modal.style.display = "none";
  modal.classList.remove("ativo");
}

// 👉 Exibe o passo atual do formulário (step-1, step-2, etc)
export function mostrarProximoStep(n) {
  for (let i = 1; i <= 3; i++) {
    const el = document.getElementById(`step-${i}`);
    if (el) el.style.display = (i === n) ? "block" : "none";
  }
}

// 🟡 Garante que o botão com onclick funcione (como <button onclick="mostrarProximoStep(2)">)
window.mostrarProximoStep = mostrarProximoStep;
