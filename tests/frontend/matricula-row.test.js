import { beforeEach, describe, expect, it } from "vitest";
import { within } from "@testing-library/dom";

import "../../static/utils.js";

const { buildMatriculaRow } = globalThis.JJUtils;

/**
 * "Componente" de teste: em vez de subir a SPA inteira, renderizamos no jsdom
 * apenas o HTML de uma linha da tabela e consultamos o DOM como um usuário.
 */
function renderLinha(matricula) {
  document.body.innerHTML = `
    <table>
      <tbody>${buildMatriculaRow(matricula)}</tbody>
    </table>
  `;
  return document.querySelector("tr");
}

describe("buildMatriculaRow", () => {
  beforeEach(() => {
    document.body.innerHTML = "";
  });

  it("renderiza os dados principais da matrícula", () => {
    const row = renderLinha({
      id: 7,
      nome_aluno: "Rickson Gracie",
      cpf: "123.456.789-00",
      id_curso: 1,
      curso_nome: "Jiu-Jitsu Iniciante",
      plano: "Anual",
      status: "Ativo"
    });

    expect(row).not.toBeNull();
    expect(row.id).toBe("row-matricula-7");
    expect(within(row).getByText("Rickson Gracie")).toBeTruthy();
    expect(row.querySelector("code").textContent).toBe("123.***.***-00");
    expect(within(row).getByText("Jiu-Jitsu Iniciante")).toBeTruthy();
    expect(within(row).getByText("Anual")).toBeTruthy();
    expect(row.querySelector(".badge-status").textContent).toBe("Ativo");
    expect(row.querySelector(".badge-status").classList.contains("status-ativo")).toBe(true);
  });

  it("escapa o nome do aluno para evitar XSS", () => {
    const row = renderLinha({
      id: 8,
      nome_aluno: '<img src=x onerror="alert(1)">',
      cpf: "123.456.789-00",
      id_curso: 1,
      curso_nome: "Curso <Teste>",
      plano: "Mensal",
      status: "Ativo"
    });

    expect(row.querySelector("img")).toBeNull();
    expect(row.innerHTML).not.toContain("<img");
    expect(row.textContent).toContain('<img src=x onerror="alert(1)">');
  });

  it("exibe 'Ativar' para matrícula inativa e esconde 'Inativar'", () => {
    const row = renderLinha({
      id: 9,
      nome_aluno: "Aluno Inativo",
      cpf: "999.888.777-66",
      id_curso: 2,
      curso_nome: "Jiu-Jitsu Competição",
      plano: "Semestral",
      status: "Inativo"
    });

    expect(within(row).getByTitle("Ativar")).toBeTruthy();
    expect(within(row).queryByTitle("Inativar")).toBeNull();
    expect(within(row).getByTitle("Cancelar")).toBeTruthy();
  });

  it("não permite cancelar novamente uma matrícula já cancelada", () => {
    const row = renderLinha({
      id: 10,
      nome_aluno: "Aluno Cancelado",
      cpf: "111.222.333-44",
      id_curso: 3,
      curso_nome: "Jiu-Jitsu Kids",
      plano: "Mensal",
      status: "Cancelado"
    });

    expect(within(row).getByTitle("Ativar")).toBeTruthy();
    expect(within(row).queryByTitle("Cancelar")).toBeNull();
    expect(within(row).getByTitle("Excluir Matrícula")).toBeTruthy();
  });
});
