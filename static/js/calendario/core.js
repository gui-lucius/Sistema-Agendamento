import { carregarAgendamentos, carregarBloqueios, mapEventos } from "./eventos.js";
import { abrirModal } from "./modal.js";
import { isoFromString, mostrarMensagemGlobal } from "./utils.js";

export async function initCalendar(barbeiroId, loading) {
  let indisponiveis = [];

  const calendar = new FullCalendar.Calendar(document.getElementById('calendar'), {
    initialView: 'timeGridWeek',
    locale: 'pt-br',
    timeZone: 'local',

    headerToolbar: {
      left: 'prev,next today',
      center: 'title',
      right: 'timeGridWeek,dayGridMonth'
    },

    businessHours: [
      {
        daysOfWeek: [1, 2, 3, 4, 5, 6],
        startTime: '09:00',
        endTime: '21:00'
      }
    ],

    slotMinTime: '09:00:00',
    slotMaxTime: '21:00:00',
    slotDuration: '01:00:00',
    slotLabelInterval: '01:00',
    contentHeight: 'auto',

    slotLabelFormat: {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    },

    allDaySlot: false,
    hiddenDays: [0], 
    selectable: true,
    selectOverlap: false,

    select(info) {
      const horario = isoFromString(info.startStr);
      if (indisponiveis.includes(horario)) {
        mostrarMensagemGlobal("Este horário já está ocupado ou bloqueado!");
        return;
      }
      abrirModal(info.startStr);
    },

    eventClick(info) {
      const status = info.event.extendedProps.status;
      const mensagens = {
        bloqueado: "⛔ Este horário está bloqueado.",
        pendente: "⏳ Aguardando confirmação.",
        aceito: "✅ Já reservado. Escolha outro horário."
      };
      alert(mensagens[status] || "ℹ️ Evento indefinido.");
    },

    events: async (_, success, fail) => {
      try {
        loading.style.display = "flex";
        const [ags, bls] = await Promise.all([
          carregarAgendamentos(barbeiroId),
          carregarBloqueios(barbeiroId)
        ]);
        const mapped = mapEventos(ags, bls);
        indisponiveis = mapped.indisponiveis;
        success(mapped.eventos);
      } catch (err) {
        mostrarMensagemGlobal("Erro ao carregar eventos!");
        fail(err);
      } finally {
        loading.style.display = "none";
      }
    }
  });

  calendar.render();
  return calendar;
}
