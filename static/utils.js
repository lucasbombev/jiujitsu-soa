/**
 * utils.js - Funções utilitárias puras do front-end.
 *
 * Este arquivo é carregado como script clássico no navegador (expõe
 * `window.JJUtils`) e também exporta via CommonJS para ser testado no
 * Vitest/Node. Manter as funções puras aqui permite testá-las sem precisar
 * simular toda a SPA ou a API.
 */
(function (root, factory) {
  const api = factory();

  if (typeof module === "object" && module.exports) {
    module.exports = api;
  }

  if (root) {
    root.JJUtils = api;
  }
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  /**
   * Escapa caracteres HTML para evitar XSS ao interpolar dados da API.
   * @param {*} value
   * @returns {string}
   */
  function escapeHtml(value) {
    if (!value) return "";
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  /**
   * Mascara o CPF para exibição na tabela (LGPD).
   * Ex.: "123.456.789-00" -> "123.***.***-00".
   * @param {string} cpf
   * @returns {string}
   */
  function maskDisplayCpf(cpf) {
    const original = cpf == null ? "" : String(cpf);
    const digits = original.replace(/\D/g, "");
    if (digits.length >= 11) {
      return `${digits.slice(0, 3)}.***.***-${digits.slice(-2)}`;
    }
    return original;
  }

  /**
   * Formata um número como moeda brasileira (BRL).
   * @param {number|string} value
   * @returns {string}
   */
  function formatCurrency(value) {
    const number = Number(value);
    return new Intl.NumberFormat("pt-BR", {
      style: "currency",
      currency: "BRL"
    }).format(Number.isFinite(number) ? number : 0);
  }

  /**
   * Gera a classe CSS do badge de status.
   * @param {string} status
   * @returns {string}
   */
  function statusClass(status) {
    const normalized = String(status || "ativo")
      .toLowerCase()
      .replace(/[^a-z0-9-]/g, "");
    return `status-${normalized}`;
  }

  /**
   * Filtra matrículas por nome/CPF e por status.
   * @param {Array<object>} matriculas
   * @param {string} search
   * @param {string} status
   * @returns {Array<object>}
   */
  function filterMatriculas(matriculas, search = "", status = "") {
    const term = String(search || "").toLowerCase().trim();
    const list = Array.isArray(matriculas) ? matriculas : [];

    return list.filter((matricula) => {
      const nome = String(matricula.nome_aluno || "").toLowerCase();
      const cpf = String(matricula.cpf || "");
      const matchesTerm = nome.includes(term) || cpf.includes(term);
      const matchesStatus = !status || matricula.status === status;
      return matchesTerm && matchesStatus;
    });
  }

  /**
   * Monta o HTML de uma linha da tabela de matrículas.
   * Função pura: recebe o objeto da API e devolve a string HTML.
   * @param {object} matricula
   * @returns {string}
   */
  function buildMatriculaRow(matricula) {
    const m = matricula || {};
    const status = m.status || "Ativo";
    const id = m.id;
    const cursoNome = m.curso_nome || `Curso #${m.id_curso}`;

    const botaoStatus =
      status !== "Ativo"
        ? `<button class="btn-table-action" onclick="alterarStatusMatricula(${id}, 'Ativo')" title="Ativar">Ativar</button>`
        : `<button class="btn-table-action" onclick="alterarStatusMatricula(${id}, 'Inativo')" title="Inativar">Inativar</button>`;

    const botaoCancelar =
      status !== "Cancelado"
        ? `<button class="btn-table-action" onclick="alterarStatusMatricula(${id}, 'Cancelado')" title="Cancelar">Cancelar</button>`
        : "";

    return `
      <tr id="row-matricula-${escapeHtml(id)}">
        <td><strong>#${escapeHtml(id)}</strong></td>
        <td><strong>${escapeHtml(m.nome_aluno)}</strong></td>
        <td><code>${maskDisplayCpf(m.cpf)}</code></td>
        <td>${escapeHtml(cursoNome)}</td>
        <td><span class="badge-mini">${escapeHtml(m.plano)}</span></td>
        <td><span class="badge-status ${statusClass(status)}">${escapeHtml(status)}</span></td>
        <td>
          <div class="action-btn-group">
            ${botaoStatus}
            ${botaoCancelar}
            <button class="btn-table-action btn-delete" onclick="deletarMatricula(${id})" title="Excluir Matrícula">🗑️</button>
          </div>
        </td>
      </tr>
    `;
  }

  return {
    escapeHtml,
    maskDisplayCpf,
    formatCurrency,
    statusClass,
    filterMatriculas,
    buildMatriculaRow
  };
});
