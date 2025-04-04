document.addEventListener('DOMContentLoaded', async function () {
  console.log("🛠️ Rodando JS LOCAL atualizado");

  const calendarEl = document.getElementById('calendar');
  const modal = document.getElementById("reservaModal");
  const loading = document.getElementById("loading");
  let selectedDate = "";
  let eventosIndisponiveis = [];

  function mostrarMensagemGlobal(texto, tipo) {
    const mensagemGlobal = document.getElementById("mensagem-global");
    mensagemGlobal.textContent = texto;
    mensagemGlobal.className = tipo === "sucesso" ? "sucesso" : "erro";
    mensagemGlobal.style.display = "block";

    setTimeout(() => {
      mensagemGlobal.style.display = "none";
    }, 4000);
  }

  const calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: 'timeGridWeek',
    headerToolbar: {
      left: 'prev,next today',
      center: 'title',
      right: 'timeGridWeek,dayGridMonth'
    },
    locale: 'pt-br',
    timeZone: 'local',
    slotMinTime: '09:00:00',
    slotMaxTime: '21:00:00',
    slotDuration: '01:00:00',
    slotLabelInterval: '01:00:00',
    slotLabelFormat: { hour: '2-digit', minute: '2-digit', hour12: false },
    allDaySlot: false,
    dayHeaderFormat: { weekday: 'short' },
    contentHeight: 'auto',
    selectable: true,
    unselectAuto: false,
    selectOverlap: false,
    snapDuration: '01:00:00',
    dragScroll: false,
    businessHours: [
      { daysOfWeek: [0, 1, 2, 3, 4, 5, 6], startTime: '09:00', endTime: '21:00' }
    ],
    select(info) {
      const horarioSelecionado = new Date(info.startStr).toISOString();
      const existe = eventosIndisponiveis.includes(horarioSelecionado);

      if (existe) {
        mostrarMensagemGlobal("Este horário já está ocupado ou bloqueado!", "erro");
        return;
      }

      selectedDate = info.startStr;
      abrirModal(selectedDate);
    },
    eventClick(info) {
      return false;
    },
    events: async function (fetchInfo, successCallback, failureCallback) {
      try {
        loading.style.display = "flex";
        const responseAgendamentos = await fetch('/api/horarios/', {
          headers: {
            "Authorization": `Bearer ${ACCESS_TOKEN}`
          }
        });
        const responseBloqueios = await fetch('/api/bloqueios/', {
          headers: {
            "Authorization": `Bearer ${ACCESS_TOKEN}`
          }
        });

        if (responseAgendamentos.ok && responseBloqueios.ok) {
          const dataAgendamentos = await responseAgendamentos.json();
          const dataBloqueios = await responseBloqueios.json();

          eventosIndisponiveis = [];

          const eventsAgendamentos = dataAgendamentos.map(horario => {
            const start = new Date(horario.data_horario_reserva);
            eventosIndisponiveis.push(start.toISOString());

            const end = new Date(start.getTime() + 60 * 60 * 1000);
            const backgroundColor = horario.status === 'pendente' ? '#ffc107' : '#28a745';
            const title = horario.status === 'pendente' ? 'Aguardando Confirmação' : 'Horário Confirmado';

            return {
              title,
              start: start.toISOString(),
              end: end.toISOString(),
              allDay: false,
              backgroundColor,
              borderColor: backgroundColor,
              clickable: false
            };
          });

          const eventsBloqueios = dataBloqueios.map(bloqueio => {
            const start = new Date(bloqueio.data_horario);
            eventosIndisponiveis.push(start.toISOString());

            return {
              title: "Indisponível",
              start: start.toISOString(),
              allDay: false,
              backgroundColor: "#FF4D4D",
              borderColor: "#FF0000",
              textColor: "FFFFFF",
              clickable: false
            };
          });

          successCallback([...eventsAgendamentos, ...eventsBloqueios]);
        } else {
          mostrarMensagemGlobal("Erro ao carregar eventos!", "erro");
        }
      } catch (error) {
        console.error('❌ Erro ao carregar eventos:', error);
        failureCallback(error);
      } finally {
        loading.style.display = "none";
      }
    }
  });

  document.getElementById("btnReservar").addEventListener("click", function (event) {
    event.preventDefault();
    submitForm();
  });

  calendar.render();

  function abrirModal(startStr) {
    if (startStr) selectedDate = startStr;
    modal.style.display = "flex";
    modal.classList.add("ativo"); // ✅ adiciona fade-in
    document.getElementById("nome").focus();
  }

  async function submitForm() {
    if (!selectedDate) {
      mostrarMensagemGlobal("Erro: Data não selecionada!", "erro");
      return;
    }

    const nome = document.getElementById("nome").value;
    const email = document.getElementById("email").value;
    const btn = document.getElementById("btnReservar");

    if (!nome || !email) {
      mostrarMensagemGlobal("Preencha todos os campos!", "erro");
      return;
    }

    if (!selectedDate.includes("T")) {
      const dataDoCalendario = calendar.view.currentStart;
      const dataBase = new Date(dataDoCalendario);
      const [hora, minuto] = selectedDate.split(":");
      const ano = dataBase.getFullYear();
      const mes = (dataBase.getMonth() + 1).toString().padStart(2, '0');
      const dia = dataBase.getDate().toString().padStart(2, '0');
      selectedDate = `${ano}-${mes}-${dia}T${hora}:${minuto}:00`;
    }

    const dados = {
      nome_cliente: nome,
      email_cliente: email,
      data_horario_reserva: selectedDate
    };

    try {
      loading.style.display = "flex";
      btn.disabled = true;
      btn.textContent = "Enviando...";

      const response = await fetch("/api/agendamentos/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${ACCESS_TOKEN}`
        },
        body: JSON.stringify(dados)
      });

      const responseData = await response.json();

      if (!response.ok) {
        mostrarMensagemGlobal(`Erro ao enviar a reserva: ${responseData?.message || "Erro desconhecido"}`, "erro");
      } else {
        mostrarMensagemGlobal("Reserva enviada com sucesso!", "sucesso");
        fecharModal();
        calendar.refetchEvents();
      }
    } catch (error) {
      mostrarMensagemGlobal("Erro de conexão com o servidor.", "erro");
    } finally {
      loading.style.display = "none";
      btn.disabled = false;
      btn.textContent = "Reservar";
    }
  }

  function fecharModal() {
    modal.style.display = "none";
    modal.classList.remove("ativo"); // ✅ remove classe de animação
  }

  document.getElementById("cancelarModal").onclick = fecharModal;

  modal.addEventListener("click", function (event) {
    if (event.target === modal) {
      event.stopPropagation();
    }
  });
});
