import { defineConfig } from "vitest/config";

/**
 * Configuração dos testes de front-end.
 *
 * - environment "jsdom": fornece `document`, `window` e `localStorage` para
 *   testar as funções de renderização da SPA sem abrir um navegador.
 * - include: mantém o Vitest focado nos testes de front-end; os testes de
 *   backend continuam sendo executados pelo Pytest.
 * - coverage: mede apenas o arquivo de utilitários puros, que é o código
 *   efetivamente testado por esta suíte.
 */
export default defineConfig({
  test: {
    environment: "jsdom",
    include: ["tests/frontend/**/*.test.js"],
    coverage: {
      provider: "v8",
      reporter: ["text", "html"],
      reportsDirectory: "coverage",
      include: ["static/utils.js"]
    }
  }
});
