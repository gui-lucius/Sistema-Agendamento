import { initCalendar } from "./core.js";
import { fecharModal, modal } from "./modal.js";
import { mostrarMensagemGlobal } from "./utils.js";
import { selectedDate } from "./modal.js";

// ✅ Overlay de Carregamento
function mostrarLoading() {
  document.getElementById('loading').style.display = 'flex';
}

function esconderLoading() {
  document.getElementById('loading').style.display = 'none';
}

// ✅ Nova mensagem visual confirmada com som
function mostrarMensagemConfirmado() {
  const popup = document.getElementById("mensagem-confirmado");
  popup.style.display = "flex";

  const audio = new Audio('/static/sounds/success.mp3');
  audio.play();

  setTimeout(() => {
    popup.style.display = "none";
  }, 3500);
}

// 🔄 Inicialização
document.addEventListener("DOMContentLoaded", () => {
  const calendarEl = document.getElementById("calendar");
  const barbeiroId = calendarEl.dataset.barbeiroId;
  let calendar;

  // Inicia o calendário
  initCalendar(barbeiroId, document.getElementById("loading"))
    .then(c => calendar = c);

  // Fecha modal
  document.getElementById("cancelarModal").addEventListener("click", fecharModal);

  // Botão de reservar
  const btnReservar = document.getElementById("btnReservar");

  btnReservar.addEventListener("click", async (e) => {
    e.preventDefault();

    const nome = document.getElementById("nome")?.value;
    const email = document.getElementById("email")?.value;
    const telefone = document.getElementById("telefone")?.value;
    const servico = document.getElementById("servico")?.value;
    const lembrete = document.getElementById("lembrete_minutos")?.value;

    if (!nome || !email || !telefone || !servico || !lembrete) {
      mostrarMensagemGlobal("Preencha todos os campos!", "erro");
      return;
    }

    const payload = {
      nome,
      email,
      telefone,
      servico,
      lembrete_minutos: lembrete,
      data_horario: selectedDate,
      barbeiro_id: barbeiroId
    };

    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
    if (!csrfToken) {
      console.error("❌ CSRF token não encontrado!");
      return;
    }

    try {
      mostrarLoading();

      const res = await fetch("/api/agendamentos/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken
        },
        credentials: "same-origin",
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        fecharModal();
        if (calendar) calendar.refetchEvents();

        // ✅ Aqui entra o novo visual com som
        mostrarMensagemConfirmado();
      } else {
        const errorText = await res.text();
        console.error("❌ Erro ao reservar:", errorText);
        mostrarMensagemGlobal("Erro ao realizar reserva!", "erro");
      }
    } catch (error) {
      console.error("❌ Exceção:", error);
      mostrarMensagemGlobal("Erro ao conectar com o servidor!", "erro");
    } finally {
      esconderLoading();
    }
  });
});
