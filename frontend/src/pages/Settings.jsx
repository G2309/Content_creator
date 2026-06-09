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
          Esta información se le pasa a la IA cada vez que generas contenido. Mientras más
          específica, mejor el resultado. En Fase 2 podrás autocompletar todo esto pegando
          la URL de tu sitio web.
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

      <form className="settings-form" onSubmit={onSave}>
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
            <span className="field-hint">
              Una línea describiendo cómo debe sonar el contenido.
            </span>
          </div>
        </div>

        <div className="settings-actions">
          <button type="submit" className="btn btn-primary" disabled={saving}>
            {saving ? <span className="spinner" /> : null}
            {saving ? "Guardando…" : "Guardar cambios"}
          </button>
        </div>
      </form>
    </>
  );
}
