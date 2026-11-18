import { describe, expect, it } from "vitest";

// O arquivo static/utils.js é um UMD: no navegador cria window.JJUtils e no
// Node/CommonJS exporta module.exports. Importá-lo aqui executa a factory e
// disponibiliza a API em globalThis.
import "../../static/utils.js";

const {
  escapeHtml,
  maskDisplayCpf,
  formatCurrency,
  statusClass,
  filterMatriculas
} = globalThis.JJUtils;

describe("escapeHtml", () => {
  it("escapa os caracteres perigosos de HTML", () => {
    expect(escapeHtml('<script>alert("x")</script>')).toBe(
      "&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;"
    );
    expect(escapeHtml("O'Reilly & Cia")).toBe("O&#039;Reilly &amp; Cia");
  });

  it("retorna string vazia para valores nulos/undefined", () => {
    expect(escapeHtml(null)).toBe("");
    expect(escapeHtml(undefined)).toBe("");
    expect(escapeHtml("")).toBe("");
  });
});

describe("maskDisplayCpf", () => {
  it("mascara CPF formatado", () => {
    expect(maskDisplayCpf("123.456.789-00")).toBe("123.***.***-00");
  });

  it("mascara CPF somente com dígitos", () => {
    expect(maskDisplayCpf("12345678900")).toBe("123.***.***-00");
  });

  it("devolve o valor original quando o CPF está incompleto", () => {
    expect(maskDisplayCpf("123.456")).toBe("123.456");
    expect(maskDisplayCpf("")).toBe("");
  });
});

describe("formatCurrency", () => {
  it("formata valores em reais", () => {
    expect(formatCurrency(150)).toContain("R$");
    expect(formatCurrency(150)).toContain("150,00");
    expect(formatCurrency(1234.56)).toContain("1.234,56");
  });

  it("trata valores inválidos como zero", () => {
    expect(formatCurrency(null)).toContain("0,00");
    expect(formatCurrency("abc")).toContain("0,00");
  });
});

describe("statusClass", () => {
  it("gera a classe CSS a partir do status", () => {
    expect(statusClass("Ativo")).toBe("status-ativo");
    expect(statusClass("CANCELADO")).toBe("status-cancelado");
  });

  it("remove caracteres que não pertencem a uma classe CSS", () => {
    expect(statusClass("Em análise!")).toBe("status-emanlise");
  });
});

describe("filterMatriculas", () => {
  const matriculas = [
    { nome_aluno: "Rickson Gracie", cpf: "111.222.333-44", status: "Ativo" },
    { nome_aluno: "Kyra Gracie", cpf: "222.333.444-55", status: "Ativo" },
    { nome_aluno: "Rodrigo Minotauro", cpf: "444.555.666-77", status: "Inativo" }
  ];

  it("filtra por nome sem diferenciar maiúsculas/minúsculas", () => {
    const resultado = filterMatriculas(matriculas, "gracie");
    expect(resultado).toHaveLength(2);
  });

  it("filtra por CPF", () => {
    const resultado = filterMatriculas(matriculas, "444.555");
    expect(resultado).toHaveLength(1);
    expect(resultado[0].nome_aluno).toBe("Rodrigo Minotauro");
  });

  it("filtra por status", () => {
    const resultado = filterMatriculas(matriculas, "", "Ativo");
    expect(resultado).toHaveLength(2);
    expect(resultado.every((m) => m.status === "Ativo")).toBe(true);
  });

  it("combina busca textual e status", () => {
    const resultado = filterMatriculas(matriculas, "gracie", "Ativo");
    expect(resultado).toHaveLength(2);

    const semResultado = filterMatriculas(matriculas, "gracie", "Inativo");
    expect(semResultado).toHaveLength(0);
  });

  it("retorna todas as matrículas sem filtros", () => {
    expect(filterMatriculas(matriculas)).toHaveLength(3);
  });

  it("protege contra listas ou campos ausentes", () => {
    expect(filterMatriculas(null)).toEqual([]);
    expect(filterMatriculas([{ status: "Ativo" }], "x")).toEqual([]);
  });
});
