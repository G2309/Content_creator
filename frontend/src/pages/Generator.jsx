import { useEffect, useState } from "react";
import { api } from "../api";

export default function Generator() {
  const [pains, setPains] = useState([]);
  const [formats, setFormats] = useState([]);
  const [selectedPain, setSelectedPain] = useState("");
  const [selectedFormat, setSelectedFormat] = useState("");
  const [extraIdea, setExtraIdea] = useState("");

  const [result, setResult] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    Promise.all([api.getPains(), api.getFormats()])
      .then(([p, f]) => {
        setPains(p);
        setFormats(f);
        if (f.length > 0) setSelectedFormat(f[0].id);
      })
      .catch((e) => setError(e.message));
  }, []);

  const canGenerate = selectedPain && selectedFormat && !loading;

  const run = async (variation) => {
    setError("");
    setLoading(true);
    setCopied(false);
    try {
      const res = await api.generate({
        pain_id: selectedPain,
        format_id: selectedFormat,
        extra_idea: extraIdea,
        variation,
      });
      setResult(res.content);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const copy = async () => {
    if (!result) return;
    try {
      await navigator.clipboard.writeText(result);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      setError("No se pudo copiar al portapapeles.");
    }
  };

  return (
    <>
      <header className="page-header">
        <div className="page-eyebrow">Paso 1 — Generar</div>
        <h1 className="page-title">Convierte una idea en un texto listo para publicar</h1>
        <p className="page-subtitle">
          Elige el dolor del cliente, el formato y, si quieres, añade una idea. La IA usa el
          contexto del negocio que tengas guardado para generar el texto.
        </p>
      </header>

      {error && (
        <div className="banner banner-error" style={{ marginBottom: "1.5rem" }}>
          {error}
        </div>
      )}

      <div className="generator-grid">
        <div className="generator-controls">
          <section className="card">
            <div className="card-title">Dolor del cliente</div>
            <div className="option-grid">
              {pains.map((p) => (
                <button
                  key={p.id}
                  type="button"
                  className={`option-card ${selectedPain === p.id ? "selected" : ""}`}
                  onClick={() => setSelectedPain(p.id)}
                  aria-pressed={selectedPain === p.id}
                >
                  <span className="option-card-label">{p.label}</span>
                  {p.description && (
                    <span className="option-card-desc">{p.description}</span>
                  )}
                </button>
              ))}
            </div>
          </section>

          <section className="card">
            <div className="card-title">Formato</div>
            <div className="option-grid">
              {formats.map((f) => (
                <button
                  key={f.id}
                  type="button"
                  className={`option-card ${selectedFormat === f.id ? "selected" : ""}`}
                  onClick={() => setSelectedFormat(f.id)}
                  aria-pressed={selectedFormat === f.id}
                >
                  <span className="option-card-label">{f.label}</span>
                  {f.description && (
                    <span className="option-card-desc">{f.description}</span>
                  )}
                </button>
              ))}
            </div>
          </section>

          <section className="card">
            <div className="card-title">Idea o contexto adicional (opcional)</div>
            <div className="field">
              <textarea
                className="textarea"
                rows={3}
                placeholder="Ej. quiero mencionar el envío gratis de esta semana, o el caso del cliente X…"
                value={extraIdea}
                onChange={(e) => setExtraIdea(e.target.value)}
                maxLength={2000}
              />
              <span className="field-hint">{extraIdea.length}/2000</span>
            </div>

            <div style={{ marginTop: "1.25rem", display: "flex", gap: "0.5rem" }}>
              <button
                className="btn btn-primary"
                onClick={() => run(false)}
                disabled={!canGenerate}
              >
                {loading ? <span className="spinner" /> : null}
                {loading ? "Generando…" : "Generar texto"}
              </button>
            </div>
          </section>
        </div>

        <aside className="generator-result">
          <div className="result">
            <div className="card-title">Resultado</div>

            {!result && !loading && (
              <div className="result-empty">
                Aquí aparecerá el texto generado.
              </div>
            )}

            {loading && (
              <div className="result-empty">
                <span className="spinner" style={{ marginRight: "0.5rem" }} />
                La IA está escribiendo…
              </div>
            )}

            {result && !loading && <div className="result-content">{result}</div>}

            {result && !loading && (
              <div className="result-actions">
                <button className="btn btn-secondary" onClick={copy}>
                  {copied ? "Copiado ✓" : "Copiar"}
                </button>
                <button
                  className="btn btn-ghost"
                  onClick={() => run(true)}
                  disabled={!canGenerate}
                >
                  Regenerar (otra versión)
                </button>
              </div>
            )}
          </div>
        </aside>
      </div>
    </>
  );
}
