const STATUS_CORES = {
    pendente: '#ffc107',
    aceito: '#28a745',
    bloqueado: '#FF4D4D'
  };
  
  export async function carregarAgendamentos(id) {
    const res = await fetch(`/api/horarios/${id}/`, {
      headers: { "Authorization": `Bearer ${ACCESS_TOKEN}` }
    });
    return res.ok ? res.json() : [];
  }
  
  export async function carregarBloqueios(id) {
    const res = await fetch(`/api/bloqueios/${id}/`, {
      headers: { "Authorization": `Bearer ${ACCESS_TOKEN}` }
    });
    return res.ok ? res.json() : [];
  }
  
  export function mapEventos(agendamentos, bloqueios) {
    const indisponiveis = [];
    const eventos = [];
  
    agendamentos.forEach(a => {
      const start = new Date(a.data_horario_reserva);
      const end = new Date(start.getTime() + 60 * 60 * 1000);
      indisponiveis.push(start.toISOString());
  
      eventos.push({
        title: a.status === 'pendente' ? 'Aguardando Confirmação' : 'Horário Confirmado',
        start: start.toISOString(),
        end: end.toISOString(),
        backgroundColor: STATUS_CORES[a.status],
        borderColor: STATUS_CORES[a.status],
        extendedProps: { status: a.status }
      });
    });
  
    bloqueios.forEach(b => {
      const start = new Date(b.data_horario);
      indisponiveis.push(start.toISOString());
  
      eventos.push({
        title: "Indisponível",
        start: start.toISOString(),
        backgroundColor: STATUS_CORES['bloqueado'],
        borderColor: "#FF0000",
        textColor: "#FFFFFF",
        extendedProps: { status: 'bloqueado' }
      });
    });
  
    return { eventos, indisponiveis };
  }
  