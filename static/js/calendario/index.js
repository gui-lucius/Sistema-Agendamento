import { initCalendar } from "./core.js";
import { fecharModal, modal } from "./modal.js";
import { mostrarMensagemGlobal } from "./utils.js";
import { selectedDate } from "./modal.js";

document.addEventListener("DOMContentLoaded", () => {
  const calendarEl = document.getElementById("calendar");
  const barbeiroId = calendarEl.dataset.barbeiroId;
  const loading = document.getElementById("loading");

  let calendar;

  initCalendar(barbeiroId, loading).then(c => calendar = c);

  document.getElementById("btnReservar").addEventListener("click", async (e) => {
    e.preventDefault();

    const nome = document.getElementById("nome").value;
    const email = document.getElementById("email").value;
    const telefone = document.getElementById("telefone").value; // 🆕 Novo campo
    const servico = document.getElementById("servico").value;
    const lembrete = document.getElementById("lembrete_minutos").value;

    if (!nome || !email || !telefone || !servico || !lembrete) {
      mostrarMensagemGlobal("Preencha todos os campos!", "erro");
      return;
    }

    const payload = {
      nome,
      email,
      telefone, // 🆕 Adicionado no payload
      servico,
      lembrete_minutos: lembrete,
      data_horario: selectedDate,
      barbeiro_id: barbeiroId
    };

    try {
      loading.style.display = "flex";

      const res = await fetch("/api/agendamentos/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${ACCESS_TOKEN}`
        },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        mostrarMensagemGlobal("Reserva realizada com sucesso!", "sucesso");
        fecharModal();
        if (calendar) calendar.refetchEvents();
      } else {
        mostrarMensagemGlobal("Erro ao realizar reserva!", "erro");
      }
    } catch (error) {
      console.error("Erro ao enviar reserva:", error);
      mostrarMensagemGlobal("Erro ao conectar com o servidor!", "erro");
    } finally {
      loading.style.display = "none";
    }
  });

  document.getElementById("cancelarModal").addEventListener("click", fecharModal);
});
