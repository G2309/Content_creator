import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";

export default function Generator() {
  const [pains, setPains] = useState([]);
  const [formats, setFormats] = useState([]);
  const [hooks, setHooks] = useState([]);
  const [contexts, setContexts] = useState([]);

  const [selectedPain, setSelectedPain] = useState(null);
  const [selectedFormat, setSelectedFormat] = useState("");
  const [selectedHook, setSelectedHook] = useState("");
  const [referenceIds, setReferenceIds] = useState([]);
  const [extraIdea, setExtraIdea] = useState("");

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);
  const [saving, setSaving] = useState(false);
  const [savedNotice, setSavedNotice] = useState(false);

  useEffect(() => {
    Promise.all([api.getPains(), api.getFormats(), api.getHooks(), api.getContexts()])
      .then(([p, f, h, c]) => {
        setPains(p);
        setFormats(f);
        setHooks(h);
        setContexts(c);
        if (f.length > 0) setSelectedFormat(f[0].id);
      })
      .catch((e) => setError(e.message));
  }, []);

  const isGuionVideo = selectedFormat === "guion_video";
  const primaryContext = contexts.find((c) => c.is_primary);
  const otherContexts = contexts.filter((c) => !c.is_primary);

  const canGenerate = useMemo(() => {
    if (selectedPain === null || !selectedFormat || loading) return false;
    if (isGuionVideo && !selectedHook) return false;
    return true;
  }, [selectedPain, selectedFormat, selectedHook, isGuionVideo, loading]);

  const toggleReference = (id) => {
    setReferenceIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  };

  const run = async (variation) => {
    setError("");
    setLoading(true);
    setCopied(false);
    setSavedNotice(false);
    try {
      const res = await api.generate({
        pain_id: selectedPain,
        format_id: selectedFormat,
        hook_id: isGuionVideo ? selectedHook : "",
        extra_idea: extraIdea,
        variation,
        reference_context_ids: referenceIds,
      });
      setResult(res);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const copy = async () => {
    if (!result?.content) return;
    try {
      await navigator.clipboard.writeText(result.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      setError("No se pudo copiar al portapapeles.");
    }
  };

  const saveToLibrary = async () => {
    if (!result) return;
    setSaving(true);
    setError("");
    try {
      await api.saveTemplate({
        content: result.content,
        pain_id: result.pain_id,
        format_id: result.format_id,
      });
      setSavedNotice(true);
      setTimeout(() => setSavedNotice(false), 2500);
    } catch (e) {
      setError(e.message);
    } finally {
      setSaving(false);
    }
  };

  const hasNoPains = pains.length === 0;
  const hasNoContexts = contexts.length === 0;

  return (
    <>
      <header className="page-header">
        <div className="page-eyebrow">Paso 1 — Generar</div>
        <h1 className="page-title">Convierte una idea en un texto listo para publicar</h1>
        <p className="page-subtitle">
          Elige el dolor del cliente, el formato y, si quieres, añade una idea. La IA usa el
          contexto principal del negocio para generar el texto.
        </p>
      </header>

      {error && (
        <div className="banner banner-error" style={{ marginBottom: "1.5rem" }}>
          {error}
        </div>
      )}

      {hasNoContexts && (
        <div className="banner banner-info" style={{ marginBottom: "1.5rem" }}>
          No tienes contextos del negocio configurados.{" "}
          <Link to="/ajustes/nuevo" style={{ textDecoration: "underline", fontWeight: 600 }}>
            Crea al menos uno para que la IA tenga información sobre tu marca.
          </Link>
        </div>
      )}

      {hasNoPains && (
        <div className="banner banner-info" style={{ marginBottom: "1.5rem" }}>
          No tienes dolores del cliente configurados.{" "}
          <Link to="/ajustes/dolores" style={{ textDecoration: "underline", fontWeight: 600 }}>
            Crea al menos uno para empezar a generar contenido.
          </Link>
        </div>
      )}

      {primaryContext && (
        <div className="banner banner-info" style={{ marginBottom: "1.5rem" }}>
          Generando para: <strong>{primaryContext.name}</strong>
          {primaryContext.business_name && primaryContext.business_name !== primaryContext.name && (
            <> ({primaryContext.business_name})</>
          )}
          .{" "}
          <Link to="/ajustes" style={{ textDecoration: "underline" }}>
            Cambiar contexto principal
          </Link>
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

          {isGuionVideo && (
            <section className="card">
              <div className="card-title">Tipo de gancho</div>
              <p style={{ fontSize: "0.875rem", color: "var(--color-text-muted)", marginBottom: "1rem" }}>
                Elige cómo quieres que arranque el guion. El gancho marca los primeros 2 segundos —
                lo que decide si la gente se queda o sigue de largo.
              </p>
              <div className="option-grid">
                {hooks.map((h) => (
                  <button
                    key={h.id}
                    type="button"
                    className={`option-card ${selectedHook === h.id ? "selected" : ""}`}
                    onClick={() => setSelectedHook(h.id)}
                    aria-pressed={selectedHook === h.id}
                  >
                    <span className="option-card-label">{h.label}</span>
                    {h.description && (
                      <span className="option-card-desc">{h.description}</span>
                    )}
                  </button>
                ))}
              </div>
            </section>
          )}

          {otherContexts.length > 0 && (
            <section className="card">
              <div className="card-title">Contextos de referencia (opcional)</div>
              <p style={{ fontSize: "0.875rem", color: "var(--color-text-muted)", marginBottom: "1rem" }}>
                Selecciona otros contextos (competidores, otras marcas) para que la IA los conozca.
                Útil cuando quieres pedirle comparaciones o resaltar ventajas frente a la competencia.
              </p>
              <div className="option-grid">
                {otherContexts.map((c) => (
                  <button
                    key={c.id}
                    type="button"
                    className={`option-card ${referenceIds.includes(c.id) ? "selected" : ""}`}
                    onClick={() => toggleReference(c.id)}
                    aria-pressed={referenceIds.includes(c.id)}
                  >
                    <span className="option-card-label">{c.name}</span>
                    {c.business_name && (
                      <span className="option-card-desc">{c.business_name}</span>
                    )}
                  </button>
                ))}
              </div>
              {referenceIds.length > 0 && (
                <p style={{ fontSize: "0.8125rem", color: "var(--color-accent)", marginTop: "0.75rem" }}>
                  {referenceIds.length} {referenceIds.length === 1 ? "contexto seleccionado" : "contextos seleccionados"} como referencia.
                </p>
              )}
            </section>
          )}

          <section className="card">
            <div className="card-title">Idea, contexto o CTA específico (opcional)</div>
            <div className="field">
              <textarea
                className="textarea"
                rows={4}
                placeholder={
                  referenceIds.length > 0
                    ? 'Ej: "Compara con los competidores seleccionados y resalta nuestras ventajas" o "El CTA debe ser: comenta la palabra ENVÍO"'
                    : 'Ej: "El CTA debe ser: comenta la palabra ENVÍO y te mandamos nuestras tarifas por DM"'
                }
                value={extraIdea}
                onChange={(e) => setExtraIdea(e.target.value)}
                maxLength={2000}
              />
              <span className="field-hint">
                {extraIdea.length}/2000 · Si pones un CTA aquí, la IA lo usa textualmente al final.
              </span>
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
            {isGuionVideo && !selectedHook && (
              <p style={{ fontSize: "0.8125rem", color: "var(--color-text-subtle)", marginTop: "0.5rem" }}>
                Selecciona un tipo de gancho para poder generar.
              </p>
            )}
          </section>
        </div>

        <aside className="generator-result">
          <div className="result">
            <div className="card-title">Resultado</div>

            {!result && !loading && (
              <div className="result-empty">Aquí aparecerá el texto generado.</div>
            )}

            {loading && (
              <div className="result-empty">
                <span className="spinner" style={{ marginRight: "0.5rem" }} />
                La IA está escribiendo…
              </div>
            )}

            {result && !loading && (
              <>
                <div className="result-content">{result.content}</div>
                {savedNotice && (
                  <div className="banner banner-success" style={{ marginTop: "1rem" }}>
                    Guardado en la biblioteca.
                  </div>
                )}
                <div className="result-actions">
                  <button className="btn btn-secondary" onClick={copy}>
                    {copied ? "Copiado ✓" : "Copiar"}
                  </button>
                  <button
                    className="btn btn-secondary"
                    onClick={saveToLibrary}
                    disabled={saving}
                  >
                    {saving ? <span className="spinner" /> : null}
                    {saving ? "Guardando…" : "Guardar en biblioteca"}
                  </button>
                  <button
                    className="btn btn-ghost"
                    onClick={() => run(true)}
                    disabled={!canGenerate}
                  >
                    Regenerar
                  </button>
                </div>
              </>
            )}
          </div>
        </aside>
      </div>
    </>
  );
}
