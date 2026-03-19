const tabButtons = document.querySelectorAll(".tab-btn");
const tabContents = document.querySelectorAll(".tab-content");

const buscaInput = document.getElementById("buscaExame");
const btnBuscar = document.getElementById("btnBuscar");
const resultadoExames = document.getElementById("resultadoExames");
const selectExame = document.getElementById("exame");
const formAgendamento = document.getElementById("formAgendamento");
const mensagemFormulario = document.getElementById("mensagemFormulario");
const tabelaAgendamentos = document.getElementById("tabelaAgendamentos");
const dataAgendamento = document.getElementById("dataAgendamento");

// Navegação entre abas
tabButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const target = button.dataset.tab;

    tabButtons.forEach((btn) => btn.classList.remove("active"));
    tabContents.forEach((content) => content.classList.remove("active"));

    button.classList.add("active");
    document.getElementById(target).classList.add("active");
  });
});

// Data mínima = hoje
const hoje = new Date().toISOString().split("T")[0];
dataAgendamento.min = hoje;

// Mensagens
function mostrarMensagem(texto, tipo = "info") {
  mensagemFormulario.innerHTML = `<div class="message ${tipo}">${texto}</div>`;
}

// Carrega exames no select
async function carregarExamesNoSelect() {
  try {
    const response = await fetch("/api/exames");
    const exames = await response.json();

    selectExame.innerHTML = `<option value="">Selecione um exame</option>`;

    if (!Array.isArray(exames) || exames.length === 0) {
      selectExame.innerHTML = `<option value="">Sem exames cadastrados</option>`;
      return;
    }

    exames.forEach((exame) => {
      const option = document.createElement("option");

      // Se vier string direta
      if (typeof exame === "string") {
        option.value = exame;
        option.textContent = exame;
      } else {
        option.value = exame.nome_exame || exame.nome || "";
        option.textContent = exame.nome_exame || exame.nome || "Exame";
      }

      selectExame.appendChild(option);
    });
  } catch (error) {
    selectExame.innerHTML = `<option value="">Erro ao carregar exames</option>`;
  }
}

// Busca exames
async function buscarExames() {
  const termo = buscaInput.value.trim();

  resultadoExames.innerHTML = "";

  if (!termo) {
    resultadoExames.innerHTML = `
      <div class="message info">
        Digite o nome de um exame para pesquisar.
      </div>
    `;
    return;
  }

  try {
    const response = await fetch(`/api/exames/buscar?termo=${encodeURIComponent(termo)}`);
    const resultados = await response.json();

    if (!Array.isArray(resultados) || resultados.length === 0) {
      resultadoExames.innerHTML = `
        <div class="message error">
          Nenhum exame encontrado com esse nome.
        </div>
      `;
      return;
    }

    resultados.forEach((exame) => {
      const card = document.createElement("div");
      card.classList.add("exam-card");
      card.innerHTML = `
        <h3>${exame.nome_exame || "-"}</h3>
        <p><strong>Preparo:</strong> ${exame.preparo || "-"}</p>
        <p><strong>Amostra:</strong> ${exame.amostra || "-"}</p>
        <p><strong>Prazo:</strong> ${exame.prazo || "-"}</p>
        <p><strong>Orientação:</strong> ${exame.orientacao || "-"}</p>
      `;
      resultadoExames.appendChild(card);
    });
  } catch (error) {
    resultadoExames.innerHTML = `
      <div class="message error">
        Erro ao buscar exames.
      </div>
    `;
  }
}

// Renderiza tabela
async function carregarAgendamentos() {
  try {
    const response = await fetch("/api/agendamentos");
    const dados = await response.json();

    tabelaAgendamentos.innerHTML = "";

    if (!Array.isArray(dados) || dados.length === 0) {
      tabelaAgendamentos.innerHTML = `
        <tr>
          <td colspan="7" class="empty-state">Nenhum agendamento cadastrado ainda.</td>
        </tr>
      `;
      return;
    }

    dados.forEach((item) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${item.id ?? "-"}</td>
        <td>${item.nome_paciente ?? "-"}</td>
        <td>${item.telefone ?? "-"}</td>
        <td>${item.exame ?? "-"}</td>
        <td>${item.data_agendamento ?? "-"}</td>
        <td>${item.horario ?? "-"}</td>
        <td>${item.observacoes ?? "-"}</td>
      `;
      tabelaAgendamentos.appendChild(tr);
    });
  } catch (error) {
    tabelaAgendamentos.innerHTML = `
      <tr>
        <td colspan="7" class="empty-state">Erro ao carregar agendamentos.</td>
      </tr>
    `;
  }
}

// Salvar agendamento
formAgendamento.addEventListener("submit", async (e) => {
  e.preventDefault();

  const payload = {
    nome_paciente: document.getElementById("nomePaciente").value.trim(),
    telefone: document.getElementById("telefone").value.trim(),
    exame: document.getElementById("exame").value,
    data_agendamento: document.getElementById("dataAgendamento").value,
    horario: document.getElementById("horario").value,
    observacoes: document.getElementById("observacoes").value.trim()
  };

  if (!payload.nome_paciente) {
    mostrarMensagem("Informe o nome do paciente.", "error");
    return;
  }

  if (!payload.telefone) {
    mostrarMensagem("Informe o telefone.", "error");
    return;
  }

  if (!payload.exame) {
    mostrarMensagem("Selecione um exame.", "error");
    return;
  }

  if (!payload.data_agendamento) {
    mostrarMensagem("Informe a data do agendamento.", "error");
    return;
  }

  if (!payload.horario) {
    mostrarMensagem("Informe o horário.", "error");
    return;
  }

  try {
    const response = await fetch("/api/agendamentos", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    const resultado = await response.json();

    if (!response.ok) {
      mostrarMensagem(resultado.erro || "Erro ao salvar agendamento.", "error");
      return;
    }

    formAgendamento.reset();
    dataAgendamento.min = hoje;
    mostrarMensagem(resultado.mensagem || "Agendamento salvo com sucesso!", "success");
    await carregarAgendamentos();
  } catch (error) {
    mostrarMensagem("Erro de conexão ao salvar agendamento.", "error");
  }
});

// Eventos
btnBuscar.addEventListener("click", buscarExames);

buscaInput.addEventListener("keypress", (e) => {
  if (e.key === "Enter") {
    buscarExames();
  }
});

// Inicialização
carregarExamesNoSelect();
carregarAgendamentos();