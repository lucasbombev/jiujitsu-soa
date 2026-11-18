import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { JSDOM } from "jsdom";
import { describe, expect, it, vi } from "vitest";

/**
 * Teste de fumaça da SPA: carrega o index.html real, avalia utils.js e app.js
 * no jsdom com uma API falsa e verifica se o dashboard é renderizado. Isso
 * garante que a integração entre os arquivos (ordem dos scripts, nomes das
 * funções e seletores do DOM) continua funcionando após a refatoração.
 */
describe("bootstrap da SPA", () => {
  it("carrega os scripts e renderiza cursos, métricas e matrículas", async () => {
    const raiz = process.cwd();
    const html = readFileSync(resolve(raiz, "static/index.html"), "utf8");
    const utils = readFileSync(resolve(raiz, "static/utils.js"), "utf8");
    const app = readFileSync(resolve(raiz, "static/app.js"), "utf8");

    const respostaJson = (data) => ({
      ok: true,
      status: 200,
      json: async () => data
    });

    const dom = new JSDOM(html, {
      url: "http://localhost/",
      runScripts: "dangerously",
      pretendToBeVisual: true,
      beforeParse(window) {
        window.fetch = vi.fn(async (input) => {
          const url = String(input);

          if (url.endsWith("/health")) {
            return respostaJson({
              status: "healthy",
              database: { status: "connected", engine: "sqlite" }
            });
          }

          if (url.endsWith("/api/dashboard/stats")) {
            return respostaJson({
              total_matriculas: 1,
              matriculas_ativas: 1,
              total_cursos: 1,
              faturamento_mensal_estimado: 150,
              taxa_retencao: 100
            });
          }

          if (url.endsWith("/api/cursos")) {
            return respostaJson([
              { id: 1, nome: "Jiu-Jitsu Iniciante", categoria: "Básico", valor: 150 }
            ]);
          }

          if (url.endsWith("/api/matriculas")) {
            return respostaJson([
              {
                id: 1,
                nome_aluno: "Rickson Gracie",
                cpf: "111.222.333-44",
                id_curso: 1,
                curso_nome: "Jiu-Jitsu Iniciante",
                plano: "Anual",
                status: "Ativo"
              }
            ]);
          }

          return respostaJson({});
        });
      }
    });

    // O JSDOM não busca os scripts externos por padrão; avaliamos na mesma
    // ordem em que o index.html os carrega.
    dom.window.eval(utils);
    dom.window.eval(app);
    dom.window.document.dispatchEvent(
      new dom.window.Event("DOMContentLoaded", { bubbles: true })
    );

    // Dá tempo para as promises de fetch/renderização resolverem.
    await new Promise((resolveDelay) => setTimeout(resolveDelay, 30));

    const doc = dom.window.document;
    expect(dom.window.JJUtils).toBeDefined();
    expect(String(doc.getElementById("kpi-total-cursos").innerText)).toBe("1");
    expect(String(doc.getElementById("kpi-total-matriculas").innerText)).toBe("1");
    expect(doc.getElementById("kpi-faturamento").innerText).toContain("150,00");
    expect(doc.querySelectorAll("#courses-grid .course-card")).toHaveLength(1);
    expect(doc.querySelector("#matriculas-tbody tr")).not.toBeNull();
    expect(doc.querySelector("#matriculas-tbody").textContent).toContain("Rickson Gracie");
    expect(doc.getElementById("cloud-status-text").innerText).toContain("Cloud Online");

    dom.window.close();
  });
});
