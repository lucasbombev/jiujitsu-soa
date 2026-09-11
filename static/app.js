/**
 * app.js - Lógica Front-end SPA (Vanilla JavaScript)
 * Gerencia a comunicação assíncrona com a REST API, renderização de tabelas,
 * modais, cálculo de métricas e verificação de saúde na nuvem.
 */

// Estado Global da Aplicação
const State = {
  cursos: [],
  matriculas: [],
  adminToken: localStorage.getItem("jiujitsu_admin_token") || null,
  health: null
};

// ==============================================================================
// INICIALIZAÇÃO
// ==============================================================================
document.addEventListener("DOMContentLoaded", () => {
  initEventListeners();
  checkCloudHealth();
  loadDashboardData();
  setupCpfMask();
  updateAuthUI();
});

// ==============================================================================
// EVENT LISTENERS E NAVEGAÇÃO
// ==============================================================================
function initEventListeners() {
  // Atualizar dados
  document.getElementById("btn-refresh-stats")?.addEventListener("click", () => {
    showToast("Atualizando dados da nuvem...", "info");
    loadDashboardData();
  });

  // Filtros de Matrícula
  document.getElementById("search-input")?.addEventListener("input", renderMatriculasTable);
  document.getElementById("filter-status")?.addEventListener("change", renderMatriculasTable);

  // Modais - Abertura
  document.getElementById("btn-open-matricula-modal")?.addEventListener("click", () => openModal("modal-matricula"));
  document.getElementById("btn-open-curso-modal")?.addEventListener("click", () => {
    if (!State.adminToken) {
      showToast("Cadastrar cursos exige autenticação de administrador.", "info");
      openModal("modal-admin");
      return;
    }
    openModal("modal-curso");
  });
  document.getElementById("btn-admin-auth")?.addEventListener("click", () => {
    if (State.adminToken) {
      // Logout
      State.adminToken = null;
      localStorage.removeItem("jiujitsu_admin_token");
      updateAuthUI();
      showToast("Sessão de administrador encerrada.", "info");
    } else {
      openModal("modal-admin");
    }
  });
  document.getElementById("btn-open-arch-modal")?.addEventListener("click", () => openModal("modal-arch"));
  document.getElementById("btn-ok-arch")?.addEventListener("click", () => closeModal("modal-arch"));

  // Modais - Fechamento
  document.querySelectorAll(".btn-close, .modal-actions .btn-secondary").forEach(btn => {
    btn.addEventListener("click", (e) => {
      const modal = e.target.closest(".modal-overlay");
      if (modal) closeModal(modal.id);
    });
  });

  // Fechar ao clicar no backdrop
  document.querySelectorAll(".modal-overlay").forEach(overlay => {
    overlay.addEventListener("click", (e) => {
      if (e.target === overlay) closeModal(overlay.id);
    });
  });

  // Fechar no ESC
  window.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      document.querySelectorAll(".modal-overlay.active").forEach(m => closeModal(m.id));
    }
  });

  // Formulários
  document.getElementById("form-nova-matricula")?.addEventListener("submit", handleNovaMatriculaSubmit);
  document.getElementById("form-novo-curso")?.addEventListener("submit", handleNovoCursoSubmit);
  document.getElementById("form-admin-login")?.addEventListener("submit", handleAdminLoginSubmit);
}

// ==============================================================================
// COMUNICAÇÃO COM A API (REST)
// ==============================================================================

// 1. Verificar Saúde do Serviço (Cloud Healthcheck)
async function checkCloudHealth() {
  const statusBadge = document.getElementById("cloud-status-badge");
  const statusText = document.getElementById("cloud-status-text");

  try {
    const res = await fetch("/health");
    if (!res.ok) throw new Error("Serviço indisponível");
    const data = await res.json();
    State.health = data;

    const engine = data.database?.engine?.toUpperCase() || "DB";
    statusText.innerText = `Cloud Online • ${engine}`;
    statusBadge.style.background = "rgba(16, 185, 129, 0.15)";
    statusBadge.style.color = "var(--accent-emerald)";
  } catch (err) {
    statusText.innerText = "Offline / Reconectando";
    statusBadge.style.background = "rgba(239, 68, 68, 0.15)";
    statusBadge.style.color = "var(--accent-crimson)";
  }
}

// 2. Carregar todos os dados do Dashboard
async function loadDashboardData() {
  await Promise.all([
    fetchStats(),
    fetchCursos(),
    fetchMatriculas()
  ]);
}

// Buscar Estatísticas
async function fetchStats() {
  try {
    const res = await fetch("/api/dashboard/stats");
    if (!res.ok) throw new Error("Falha ao buscar estatísticas");
    const stats = await res.json();

    document.getElementById("kpi-total-matriculas").innerText = stats.total_matriculas;
    document.getElementById("kpi-matriculas-ativas").innerText = stats.matriculas_ativas;
    document.getElementById("kpi-total-cursos").innerText = stats.total_cursos;
    document.getElementById("kpi-subtext-retencao").innerText = `Taxa de Atividade: ${stats.taxa_retencao}%`;

    // Formatar moeda BRL
    const faturamentoFormatado = new Intl.NumberFormat("pt-BR", {
      style: "currency",
      currency: "BRL"
    }).format(stats.faturamento_mensal_estimado || 0);

    document.getElementById("kpi-faturamento").innerText = faturamentoFormatado;
  } catch (err) {
    console.error("Erro stats:", err);
  }
}

// Buscar Cursos
async function fetchCursos() {
  try {
    const res = await fetch("/api/cursos");
    if (!res.ok) throw new Error("Falha ao buscar cursos");
    State.cursos = await res.json();
    renderCursos();
    populateCursoSelect();
  } catch (err) {
    console.error("Erro cursos:", err);
    document.getElementById("courses-grid").innerHTML = `
      <div class="loading-state" style="color: var(--accent-crimson);">
        Erro ao carregar cursos. Verifique a conexão com a API.
      </div>
    `;
  }
}

// Buscar Matrículas
async function fetchMatriculas() {
  try {
    const res = await fetch("/api/matriculas");
    if (!res.ok) throw new Error("Falha ao buscar matrículas");
    State.matriculas = await res.json();
    renderMatriculasTable();
  } catch (err) {
    console.error("Erro matrículas:", err);
    document.getElementById("matriculas-tbody").innerHTML = `
      <tr>
        <td colspan="7" class="loading-state" style="color: var(--accent-crimson);">
          Erro ao carregar matrículas.
        </td>
      </tr>
    `;
  }
}

// ==============================================================================
// RENDERIZAÇÃO NA INTERFACE
// ==============================================================================

// Renderizar Cards de Cursos
function renderCursos() {
  const container = document.getElementById("courses-grid");
  if (!container) return;

  if (State.cursos.length === 0) {
    container.innerHTML = `<div class="loading-state">Nenhum curso cadastrado no momento.</div>`;
    return;
  }

  container.innerHTML = State.cursos.map(c => `
    <div class="course-card" id="course-card-${c.id}">
      <div>
        <span class="course-category">${escapeHtml(c.categoria)}</span>
        <h3 class="course-title">${escapeHtml(c.nome)}</h3>
      </div>
      <div>
        <div class="course-price-box">
          <span class="course-price">R$ ${c.valor.toFixed(2)}</span>
          <span class="course-price-period"> / mês</span>
        </div>
        <button class="btn btn-secondary" style="width: 100%;" onclick="openMatriculaParaCurso(${c.id})">
          Matricular Aluno
        </button>
      </div>
    </div>
  `).join("");
}

// Preencher Dropdown de Cursos no Modal
function populateCursoSelect() {
  const select = document.getElementById("mat-curso");
  if (!select) return;

  select.innerHTML = `<option value="">Selecione um curso...</option>` +
    State.cursos.map(c => `
      <option value="${c.id}">${escapeHtml(c.nome)} (R$ ${c.valor.toFixed(2)})</option>
    `).join("");
}

// Renderizar Tabela de Matrículas com Busca e Filtros
function renderMatriculasTable() {
  const tbody = document.getElementById("matriculas-tbody");
  if (!tbody) return;

  const termoBusca = (document.getElementById("search-input")?.value || "").toLowerCase().trim();
  const statusFiltro = document.getElementById("filter-status")?.value || "";

  // Filtragem local instantânea
  const filtradas = State.matriculas.filter(m => {
    const bateNome = m.nome_aluno.toLowerCase().includes(termoBusca);
    const bateCpf = m.cpf.includes(termoBusca);
    const bateStatus = !statusFiltro || m.status === statusFiltro;
    return (bateNome || bateCpf) && bateStatus;
  });

  if (filtradas.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="7" class="loading-state">Nenhuma matrícula encontrada com os filtros atuais.</td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = filtradas.map(m => {
    const statusClass = `status-${m.status.toLowerCase()}`;
    const cpfFormatado = maskDisplayCpf(m.cpf);

    return `
      <tr id="row-matricula-${m.id}">
        <td><strong>#${m.id}</strong></td>
        <td><strong>${escapeHtml(m.nome_aluno)}</strong></td>
        <td><code>${cpfFormatado}</code></td>
        <td>${escapeHtml(m.curso_nome || "Curso #" + m.id_curso)}</td>
        <td><span class="badge-mini">${escapeHtml(m.plano)}</span></td>
        <td>
          <span class="badge-status ${statusClass}">${m.status}</span>
        </td>
        <td>
          <div class="action-btn-group">
            ${m.status !== "Ativo" ? `
              <button class="btn-table-action" onclick="alterarStatusMatricula(${m.id}, 'Ativo')" title="Ativar">
                Ativar
              </button>
            ` : `
              <button class="btn-table-action" onclick="alterarStatusMatricula(${m.id}, 'Inativo')" title="Inativar">
                Inativar
              </button>
            `}
            ${m.status !== "Cancelado" ? `
              <button class="btn-table-action" onclick="alterarStatusMatricula(${m.id}, 'Cancelado')" title="Cancelar">
                Cancelar
              </button>
            ` : ""}
            <button class="btn-table-action btn-delete" onclick="deletarMatricula(${m.id})" title="Excluir Matrícula">
              🗑️
            </button>
          </div>
        </td>
      </tr>
    `;
  }).join("");
}

// ==============================================================================
// OPERAÇÕES DE CRUD (AÇÕES)
// ==============================================================================

// Submeter Nova Matrícula
async function handleNovaMatriculaSubmit(e) {
  e.preventDefault();
  const nome = document.getElementById("mat-nome").value.trim();
  const cpf = document.getElementById("mat-cpf").value.trim();
  const id_curso = parseInt(document.getElementById("mat-curso").value, 10);
  const plano = document.getElementById("mat-plano").value;

  if (!nome || !cpf || !id_curso || !plano) {
    showToast("Por favor, preencha todos os campos obrigatórios.", "error");
    return;
  }

  try {
    const res = await fetch("/api/matriculas", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nome_aluno: nome, cpf, id_curso, plano })
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Falha ao registrar matrícula");
    }

    const nova = await res.json();
    showToast(`Matrícula de ${nova.nome_aluno} realizada com sucesso!`, "success");
    closeModal("modal-matricula");
    document.getElementById("form-nova-matricula").reset();
    
    // Atualizar dados
    loadDashboardData();
  } catch (err) {
    showToast(`Erro: ${err.message}`, "error");
  }
}

// Submeter Novo Curso (Admin)
async function handleNovoCursoSubmit(e) {
  e.preventDefault();
  if (!State.adminToken) {
    showToast("Autenticação necessária.", "error");
    openModal("modal-admin");
    return;
  }

  const nome = document.getElementById("curso-nome").value.trim();
  const categoria = document.getElementById("curso-categoria").value;
  const valor = parseFloat(document.getElementById("curso-valor").value);

  try {
    const res = await fetch("/api/cursos", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${State.adminToken}`
      },
      body: JSON.stringify({ nome, categoria, valor })
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Falha ao cadastrar curso");
    }

    showToast(`Curso "${nome}" cadastrado com sucesso!`, "success");
    closeModal("modal-curso");
    document.getElementById("form-novo-curso").reset();
    loadDashboardData();
  } catch (err) {
    showToast(`Erro ao criar curso: ${err.message}`, "error");
  }
}

// Alterar Status da Matrícula (Ativo, Inativo, Cancelado)
async function alterarStatusMatricula(id, novoStatus) {
  try {
    const res = await fetch(`/api/matriculas/${id}/status`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: novoStatus })
    });

    if (!res.ok) throw new Error("Falha ao atualizar status");
    showToast(`Matrícula #${id} alterada para ${novoStatus}.`, "success");
    loadDashboardData();
  } catch (err) {
    showToast(`Erro: ${err.message}`, "error");
  }
}

// Excluir Matrícula
async function deletarMatricula(id) {
  if (!confirm(`Tem certeza que deseja excluir permanentemente a matrícula #${id}?`)) {
    return;
  }

  try {
    const res = await fetch(`/api/matriculas/${id}`, {
      method: "DELETE"
    });

    if (!res.ok && res.status !== 204) throw new Error("Falha ao excluir matrícula");
    showToast(`Matrícula #${id} removida do banco de dados.`, "success");
    loadDashboardData();
  } catch (err) {
    showToast(`Erro: ${err.message}`, "error");
  }
}

// Submeter Login Admin
async function handleAdminLoginSubmit(e) {
  e.preventDefault();
  const username = document.getElementById("admin-user").value.trim();
  const password = document.getElementById("admin-pass").value.trim();

  try {
    const res = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });

    if (!res.ok) throw new Error("Usuário ou senha incorretos");
    const data = await res.json();
    State.adminToken = data.token;
    localStorage.setItem("jiujitsu_admin_token", data.token);

    showToast("Autenticado como Administrador com sucesso!", "success");
    closeModal("modal-admin");
    updateAuthUI();
  } catch (err) {
    showToast(`Falha no login: ${err.message}`, "error");
  }
}

function updateAuthUI() {
  const label = document.getElementById("admin-auth-label");
  const btn = document.getElementById("btn-admin-auth");
  if (!label || !btn) return;

  if (State.adminToken) {
    label.innerText = "Sair (Admin)";
    btn.style.borderColor = "var(--accent-emerald)";
    btn.style.color = "var(--accent-emerald)";
  } else {
    label.innerText = "Entrar (Admin)";
    btn.style.borderColor = "var(--border-color)";
    btn.style.color = "var(--text-main)";
  }
}

// ==============================================================================
// HELPERS E UTILITÁRIOS
// ==============================================================================

function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.add("active");
    modal.setAttribute("aria-hidden", "false");
  }
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove("active");
    modal.setAttribute("aria-hidden", "true");
  }
}

window.openMatriculaParaCurso = function(cursoId) {
  openModal("modal-matricula");
  const select = document.getElementById("mat-curso");
  if (select) select.value = cursoId;
};

// Máscara dinâmica de CPF
function setupCpfMask() {
  const cpfInput = document.getElementById("mat-cpf");
  if (!cpfInput) return;

  cpfInput.addEventListener("input", (e) => {
    let v = e.target.value.replace(/\D/g, "");
    if (v.length > 11) v = v.substring(0, 11);
    
    if (v.length > 9) {
      v = v.replace(/(\d{3})(\d{3})(\d{3})(\d{1,2})/, "$1.$2.$3-$4");
    } else if (v.length > 6) {
      v = v.replace(/(\d{3})(\d{3})(\d{1,3})/, "$1.$2.$3");
    } else if (v.length > 3) {
      v = v.replace(/(\d{3})(\d{1,3})/, "$1.$2");
    }
    e.target.value = v;
  });
}

function maskDisplayCpf(cpf) {
  const digits = cpf.replace(/\D/g, "");
  if (digits.length >= 11) {
    return `${digits.slice(0, 3)}.***.***-${digits.slice(-2)}`;
  }
  return cpf;
}

function showToast(message, type = "info") {
  const container = document.getElementById("toast-container");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `<span>${type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️'}</span> ${escapeHtml(message)}`;

  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateX(100%)";
    toast.style.transition = "all 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
