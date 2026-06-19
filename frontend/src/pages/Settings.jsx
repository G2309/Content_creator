import { useEffect, useState } from "react";
import { api } from "../api";

const EMPTY = {
  business_name: "",
  description: "",
  services: "",
  target_audience: "",
  value_proposition: "",
  tone: "",
};

export default function Settings() {
  const [form, setForm] = useState(EMPTY);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  const [url, setUrl] = useState("");
  const [extracting, setExtracting] = useState(false);
  const [extractError, setExtractError] = useState("");
  const [extractInfo, setExtractInfo] = useState(null);

  useEffect(() => {
    api
      .getContext()
      .then((data) => {
        setForm({
          business_name: data.business_name || "",
          description: data.description || "",
          services: data.services || "",
          target_audience: data.target_audience || "",
          value_proposition: data.value_proposition || "",
          tone: data.tone || "",
        });
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  const update = (key) => (e) => {
    setForm({ ...form, [key]: e.target.value });
    setSuccess(false);
  };

  const onExtract = async (e) => {
    e.preventDefault();
    if (!url.trim()) return;
    setExtractError("");
    setExtractInfo(null);
    setExtracting(true);
    try {
      const res = await api.scrapeUrl(url.trim());
      const p = res.proposed_context;
      setForm((prev) => ({
        business_name: p.business_name || prev.business_name,
        description: p.description || prev.description,
        services: p.services || prev.services,
        target_audience: p.target_audience || prev.target_audience,
        value_proposition: p.value_proposition || prev.value_proposition,
        tone: p.tone || prev.tone,
      }));
      setExtractInfo({
        pages: res.pages_scraped,
        urls: res.page_urls,
        title: res.site_title,
      });
      setSuccess(false);
    } catch (err) {
      setExtractError(err.message);
    } finally {
      setExtracting(false);
    }
  };

  const onSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError("");
    setSuccess(false);
    try {
      await api.updateContext(form);
      setSuccess(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  if (loading) return null;

  return (
    <>
      <header className="page-header">
        <div className="page-eyebrow">Configuración</div>
        <h1 className="page-title">Contexto del negocio</h1>
        <p className="page-subtitle">
          Esta información se le pasa a la IA cada vez que generas contenido. Puedes
          rellenarla a mano o autocompletarla pegando la URL de tu sitio web.
        </p>
      </header>

      {error && (
        <div className="banner banner-error" style={{ marginBottom: "1.5rem" }}>
          {error}
        </div>
      )}
      {success && (
        <div className="banner banner-success" style={{ marginBottom: "1.5rem" }}>
          Guardado correctamente.
        </div>
      )}

      <div className="settings-form">
        <section className="card">
          <div className="card-title">Importar desde URL</div>
          <p style={{ fontSize: "0.875rem", color: "var(--color-text-muted)", marginBottom: "1rem" }}>
            Pega la URL del sitio web del negocio. La app navegará por las páginas principales
            (inicio, sobre nosotros, servicios, contacto) y usará la IA para llenar los campos.
            Tarda entre 20 y 60 segundos.
          </p>

          <form onSubmit={onExtract} style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
            <input
              type="text"
              className="input"
              placeholder="https://tunegocio.com"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              disabled={extracting}
              style={{ flex: 1, minWidth: "200px" }}
            />
            <button
              type="submit"
              className="btn btn-primary"
              disabled={extracting || !url.trim()}
            >
              {extracting ? <span className="spinner" /> : null}
              {extracting ? "Extrayendo…" : "Extraer datos"}
            </button>
          </form>

          {extracting && (
            <p style={{ fontSize: "0.8125rem", color: "var(--color-text-subtle)", marginTop: "0.75rem" }}>
              Navegando el sitio y analizando el contenido. No cierres esta pestaña.
            </p>
          )}

          {extractError && (
            <div className="banner banner-error" style={{ marginTop: "1rem" }}>
              {extractError}
            </div>
          )}

          {extractInfo && (
            <div className="banner banner-info" style={{ marginTop: "1rem", flexDirection: "column", alignItems: "flex-start", gap: "0.5rem" }}>
              <div>
                <strong>Listo.</strong> Se analizaron {extractInfo.pages} páginas
                {extractInfo.title ? <> de <em>{extractInfo.title}</em></> : null}.
                Revisa los campos y guarda los cambios.
              </div>
              <details style={{ fontSize: "0.8125rem", marginTop: "0.25rem" }}>
                <summary style={{ cursor: "pointer" }}>Ver URLs analizadas</summary>
                <ul style={{ margin: "0.5rem 0 0 1rem", padding: 0, fontFamily: "var(--font-mono)" }}>
                  {extractInfo.urls.map((u) => (
                    <li key={u} style={{ wordBreak: "break-all" }}>{u}</li>
                  ))}
                </ul>
              </details>
            </div>
          )}
        </section>

        <form onSubmit={onSave} className="settings-form">
          <div className="card">
            <div className="field">
              <label className="field-label" htmlFor="business_name">Nombre del negocio</label>
              <input
                id="business_name"
                className="input"
                value={form.business_name}
                onChange={update("business_name")}
                maxLength={255}
                placeholder="Ej. UsaProShop"
              />
            </div>
          </div>

          <div className="card">
            <div className="field">
              <label className="field-label" htmlFor="description">Descripción del negocio</label>
              <textarea
                id="description"
                className="textarea"
                rows={3}
                value={form.description}
                onChange={update("description")}
                maxLength={5000}
                placeholder="A qué se dedica el negocio en 2-3 líneas."
              />
            </div>
          </div>

          <div className="card">
            <div className="field">
              <label className="field-label" htmlFor="services">Servicios o productos</label>
              <textarea
                id="services"
                className="textarea"
                rows={4}
                value={form.services}
                onChange={update("services")}
                maxLength={5000}
                placeholder="Qué ofrecen, separado por líneas o comas."
              />
            </div>
          </div>

          <div className="card">
            <div className="field">
              <label className="field-label" htmlFor="target_audience">A quién le hablan</label>
              <textarea
                id="target_audience"
                className="textarea"
                rows={3}
                value={form.target_audience}
                onChange={update("target_audience")}
                maxLength={5000}
                placeholder="Describe al cliente ideal — quién es, qué hace, qué le preocupa."
              />
            </div>
          </div>

          <div className="card">
            <div className="field">
              <label className="field-label" htmlFor="value_proposition">Propuesta de valor</label>
              <textarea
                id="value_proposition"
                className="textarea"
                rows={3}
                value={form.value_proposition}
                onChange={update("value_proposition")}
                maxLength={5000}
                placeholder="Qué los hace diferentes — el porqué deberían elegirlos a ustedes."
              />
            </div>
          </div>

          <div className="card">
            <div className="field">
              <label className="field-label" htmlFor="tone">Tono de voz</label>
              <input
                id="tone"
                className="input"
                value={form.tone}
                onChange={update("tone")}
                maxLength={255}
                placeholder="Ej. cercano, claro y directo, sin tecnicismos."
              />
              <span className="field-hint">Una línea describiendo cómo debe sonar el contenido.</span>
            </div>
          </div>

          <div className="settings-actions">
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saving ? <span className="spinner" /> : null}
              {saving ? "Guardando…" : "Guardar cambios"}
            </button>
          </div>
        </form>
      </div>
    </>
  );
}
