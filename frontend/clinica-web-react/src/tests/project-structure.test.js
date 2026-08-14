import { describe, expect, it } from "vitest";
import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";

const projectFile = (path) => resolve(process.cwd(), path);

describe("Estructura principal de INEO Web", () => {
  it.each([
    "src/main.jsx",
    "src/router/AppRouter.jsx",
    "src/context/AuthContext.jsx",
    "src/context/PatientContext.jsx",
  ])("debe incluir %s", (file) => {
    expect(existsSync(projectFile(file))).toBe(true);
  });

  it.each([
    "src/pages/administrativo",
    "src/pages/enfermeria",
    "src/pages/medico",
    "src/pages/estudios",
  ])("debe incluir el módulo %s", (directory) => {
    expect(existsSync(projectFile(directory))).toBe(true);
  });

  it("debe conservar la configuración de la API", () => {
    expect(existsSync(projectFile("src/services/api.js"))).toBe(true);

    const apiService = readFileSync(projectFile("src/services/api.js"), "utf8");

    expect(apiService).toContain("/api/v1");
  });

  it("debe incluir rutas privadas para usuarios autenticados", () => {
    const router = readFileSync(
      projectFile("src/router/AppRouter.jsx"),
      "utf8",
    );

    expect(router).toMatch(/PrivateRoute|ProtectedRoute|RequireAuth/);
    expect(router).toContain("isAuthenticated");
    expect(router).toContain('<Navigate to="/login" replace />');
  });
});
