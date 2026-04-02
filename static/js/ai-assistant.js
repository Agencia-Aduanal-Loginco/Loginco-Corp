/**
 * ai-assistant.js — Asistente IA para el admin de Loginco Corp
 * Inserta un botón "Generar con IA" en el formulario de Post del admin Django (Unfold).
 * Abre un modal vanilla JS, recopila contexto del formulario y llama al endpoint AJAX.
 */

(function () {
  "use strict";

  // ---------------------------------------------------------------------------
  // Utilidades
  // ---------------------------------------------------------------------------

  function getCsrfToken() {
    const match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? match[1] : "";
  }

  function showToast(message, type) {
    // type: 'success' | 'warning' | 'error'
    const colors = {
      success: "#16a34a",
      warning: "#d97706",
      error: "#dc2626",
    };

    const toast = document.createElement("div");
    toast.textContent = message;
    Object.assign(toast.style, {
      position: "fixed",
      bottom: "24px",
      right: "24px",
      background: colors[type] || colors.success,
      color: "#fff",
      padding: "12px 20px",
      borderRadius: "8px",
      boxShadow: "0 4px 12px rgba(0,0,0,0.2)",
      fontSize: "14px",
      fontWeight: "500",
      zIndex: "9999",
      maxWidth: "360px",
      lineHeight: "1.4",
      transition: "opacity 0.4s ease",
      opacity: "1",
    });

    document.body.appendChild(toast);

    setTimeout(function () {
      toast.style.opacity = "0";
      setTimeout(function () {
        if (toast.parentNode) toast.parentNode.removeChild(toast);
      }, 400);
    }, 4000);
  }

  // ---------------------------------------------------------------------------
  // Modal
  // ---------------------------------------------------------------------------

  function createModal() {
    // Backdrop
    const backdrop = document.createElement("div");
    Object.assign(backdrop.style, {
      position: "fixed",
      inset: "0",
      background: "rgba(0,0,0,0.5)",
      zIndex: "8000",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
    });

    // Caja del modal
    const box = document.createElement("div");
    Object.assign(box.style, {
      background: "#fff",
      borderRadius: "8px",
      padding: "28px 32px",
      width: "480px",
      maxWidth: "90vw",
      boxShadow: "0 8px 32px rgba(0,0,0,0.18)",
      fontFamily: "inherit",
    });

    // Título
    const title = document.createElement("h2");
    title.textContent = "Asistente IA — Loginco";
    Object.assign(title.style, {
      margin: "0 0 20px",
      fontSize: "18px",
      fontWeight: "600",
      color: "#0f172a",
    });

    // Label + select de tipo
    const typeLabel = document.createElement("label");
    typeLabel.textContent = "Tipo de generación";
    Object.assign(typeLabel.style, {
      display: "block",
      fontSize: "13px",
      fontWeight: "500",
      color: "#374151",
      marginBottom: "6px",
    });

    const typeSelect = document.createElement("select");
    Object.assign(typeSelect.style, {
      width: "100%",
      padding: "8px 12px",
      borderRadius: "6px",
      border: "1px solid #d1d5db",
      fontSize: "14px",
      color: "#111827",
      marginBottom: "16px",
      outline: "none",
    });

    const typeOptions = [
      { value: "full_post", label: "Artículo completo" },
      { value: "meta_only", label: "Solo metadatos SEO" },
      { value: "excerpt", label: "Resumen (excerpt)" },
      { value: "improve", label: "Mejorar texto existente" },
    ];
    typeOptions.forEach(function (opt) {
      const option = document.createElement("option");
      option.value = opt.value;
      option.textContent = opt.label;
      typeSelect.appendChild(option);
    });

    // Keywords (solo para full_post)
    const keywordsWrapper = document.createElement("div");
    Object.assign(keywordsWrapper.style, { marginBottom: "16px" });

    const keywordsLabel = document.createElement("label");
    keywordsLabel.textContent = "Keywords adicionales (opcional)";
    Object.assign(keywordsLabel.style, {
      display: "block",
      fontSize: "13px",
      fontWeight: "500",
      color: "#374151",
      marginBottom: "6px",
    });

    const keywordsInput = document.createElement("input");
    keywordsInput.type = "text";
    keywordsInput.placeholder = "ej. importación temporal, IMMEX, maquila";
    Object.assign(keywordsInput.style, {
      width: "100%",
      padding: "8px 12px",
      borderRadius: "6px",
      border: "1px solid #d1d5db",
      fontSize: "14px",
      color: "#111827",
      outline: "none",
      boxSizing: "border-box",
    });

    keywordsWrapper.appendChild(keywordsLabel);
    keywordsWrapper.appendChild(keywordsInput);

    // Mostrar/ocultar keywords según tipo
    function toggleKeywords() {
      keywordsWrapper.style.display = typeSelect.value === "full_post" ? "block" : "none";
    }
    typeSelect.addEventListener("change", toggleKeywords);
    toggleKeywords();

    // Botones
    const btnRow = document.createElement("div");
    Object.assign(btnRow.style, {
      display: "flex",
      justifyContent: "flex-end",
      gap: "12px",
      marginTop: "8px",
    });

    const cancelBtn = document.createElement("button");
    cancelBtn.type = "button";
    cancelBtn.textContent = "Cancelar";
    Object.assign(cancelBtn.style, {
      padding: "8px 18px",
      borderRadius: "6px",
      border: "1px solid #d1d5db",
      background: "#fff",
      color: "#374151",
      fontSize: "14px",
      cursor: "pointer",
    });

    const generateBtn = document.createElement("button");
    generateBtn.type = "button";
    generateBtn.textContent = "Generar";
    Object.assign(generateBtn.style, {
      padding: "8px 20px",
      borderRadius: "6px",
      border: "none",
      background: "#0ea5e9",
      color: "#fff",
      fontSize: "14px",
      fontWeight: "600",
      cursor: "pointer",
    });

    btnRow.appendChild(cancelBtn);
    btnRow.appendChild(generateBtn);

    box.appendChild(title);
    box.appendChild(typeLabel);
    box.appendChild(typeSelect);
    box.appendChild(keywordsWrapper);
    box.appendChild(btnRow);
    backdrop.appendChild(box);

    return { backdrop, typeSelect, keywordsInput, cancelBtn, generateBtn };
  }

  // ---------------------------------------------------------------------------
  // Recopilación de contexto del formulario
  // ---------------------------------------------------------------------------

  function buildContext(generationType, keywords) {
    const titleEl = document.getElementById("id_title");
    const bodyEl = document.getElementById("id_body");
    const siteTargetsEl = document.getElementById("id_site_targets");
    const categoryEl = document.getElementById("id_category");

    const title = titleEl ? titleEl.value.trim() : "";
    const body = bodyEl ? bodyEl.value : "";

    // Obtener el primer site_target seleccionado
    let siteTargetName = "";
    let siteTargetSlug = "";
    if (siteTargetsEl) {
      const selectedOption = siteTargetsEl.querySelector("option:checked") ||
        Array.from(siteTargetsEl.options).find(function (o) { return o.selected; });
      if (selectedOption) {
        siteTargetName = selectedOption.textContent.trim();
        // Intentar obtener el slug del data attribute o inferirlo del texto
        siteTargetSlug = selectedOption.dataset.slug || "";
      }
    }

    // Texto plano del body (strip HTML básico)
    const bodyText = body.replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();

    // Nombre de categoría
    let categoryName = "";
    if (categoryEl) {
      const selectedCat = categoryEl.options[categoryEl.selectedIndex];
      if (selectedCat) categoryName = selectedCat.textContent.trim();
    }

    const ctx = {
      title: title,
      site_target_name: siteTargetName,
      site_target_slug: siteTargetSlug,
    };

    if (generationType === "full_post") {
      ctx.category = categoryName;
      ctx.keywords = keywords;
      ctx.word_count = 1000;
    } else if (generationType === "meta_only") {
      ctx.body_text = bodyText.slice(0, 500);
    } else if (generationType === "excerpt") {
      ctx.body_text = bodyText.slice(0, 300);
    } else if (generationType === "improve") {
      ctx.body = body;
    }

    return ctx;
  }

  // ---------------------------------------------------------------------------
  // Inyección de resultados en el formulario
  // ---------------------------------------------------------------------------

  function fillFormFields(generationType, data) {
    function setField(id, value) {
      const el = document.getElementById(id);
      if (!el || value === undefined || value === null) return;
      el.value = value;
      el.dispatchEvent(new Event("input", { bubbles: true }));
      el.dispatchEvent(new Event("change", { bubbles: true }));
    }

    if (generationType === "full_post") {
      setField("id_body", data.body || "");
      setField("id_meta_title", data.meta_title || "");
      setField("id_meta_description", data.meta_description || "");
      setField("id_excerpt", data.excerpt || "");

      // Marcar ai_generated como checked
      const aiGenField = document.getElementById("id_ai_generated");
      if (aiGenField) aiGenField.checked = true;

      // Notificar al editor TipTap para que actualice su vista
      if (data.body) {
        document.dispatchEvent(
          new CustomEvent("tiptap:set-content", { detail: { content: data.body } })
        );
      }
    } else if (generationType === "meta_only") {
      setField("id_meta_title", data.meta_title || "");
      setField("id_meta_description", data.meta_description || "");
    } else if (generationType === "excerpt") {
      setField("id_excerpt", data.excerpt || "");
    } else if (generationType === "improve") {
      setField("id_body", data.body || "");
      if (data.body) {
        document.dispatchEvent(
          new CustomEvent("tiptap:set-content", { detail: { content: data.body } })
        );
      }
    }
  }

  // ---------------------------------------------------------------------------
  // Lógica principal: insertar botón y manejar flujo
  // ---------------------------------------------------------------------------

  function initAiAssistant() {
    const bodyField = document.getElementById("id_body");
    if (!bodyField) return; // No estamos en el formulario de Post

    // Encontrar el wrapper del campo body en Unfold
    const bodyWrapper = bodyField.closest(".form-row") ||
      bodyField.closest("[class*='field-body']") ||
      bodyField.parentNode;

    if (!bodyWrapper) return;

    // Crear botón "Generar con IA"
    const aiBtn = document.createElement("button");
    aiBtn.type = "button";
    aiBtn.textContent = "✨ Generar con IA";
    Object.assign(aiBtn.style, {
      display: "inline-flex",
      alignItems: "center",
      gap: "6px",
      padding: "8px 16px",
      marginBottom: "12px",
      borderRadius: "6px",
      border: "none",
      background: "#0ea5e9",
      color: "#fff",
      fontSize: "14px",
      fontWeight: "600",
      cursor: "pointer",
      transition: "background 0.2s",
    });

    aiBtn.addEventListener("mouseenter", function () {
      aiBtn.style.background = "#0284c7";
    });
    aiBtn.addEventListener("mouseleave", function () {
      aiBtn.style.background = "#0ea5e9";
    });

    // Insertar antes del wrapper del body
    bodyWrapper.parentNode.insertBefore(aiBtn, bodyWrapper);

    // Manejar clic en el botón
    aiBtn.addEventListener("click", function () {
      const modal = createModal();
      document.body.appendChild(modal.backdrop);

      // Cerrar al hacer clic en el backdrop (fuera de la caja)
      modal.backdrop.addEventListener("click", function (e) {
        if (e.target === modal.backdrop) closeModal();
      });

      modal.cancelBtn.addEventListener("click", closeModal);

      function closeModal() {
        if (modal.backdrop.parentNode) {
          modal.backdrop.parentNode.removeChild(modal.backdrop);
        }
      }

      modal.generateBtn.addEventListener("click", function () {
        const generationType = modal.typeSelect.value;
        const keywords = modal.keywordsInput.value.trim();
        const context = buildContext(generationType, keywords);

        // Mostrar spinner en el botón
        const originalText = modal.generateBtn.textContent;
        modal.generateBtn.textContent = "Generando…";
        modal.generateBtn.disabled = true;
        modal.cancelBtn.disabled = true;

        fetch("/admin/ai/generate/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCsrfToken(),
          },
          body: JSON.stringify({
            generation_type: generationType,
            context: context,
          }),
        })
          .then(function (response) {
            return response.json().then(function (data) {
              return { ok: response.ok, status: response.status, data: data };
            });
          })
          .then(function (result) {
            closeModal();

            if (result.ok && result.data.success) {
              fillFormFields(generationType, result.data.data);
              const totalTokens = (result.data.tokens.input || 0) + (result.data.tokens.output || 0);
              showToast(
                "✓ Contenido generado — " + totalTokens + " tokens usados",
                "success"
              );
            } else if (result.status === 429) {
              showToast(
                result.data.error || "Límite de generaciones alcanzado.",
                "warning"
              );
            } else {
              showToast(
                result.data.error || "Error al generar contenido.",
                "error"
              );
            }
          })
          .catch(function (err) {
            closeModal();
            showToast("Error de red al contactar el asistente IA.", "error");
            console.error("[AI Assistant]", err);
          });
      });
    });
  }

  // ---------------------------------------------------------------------------
  // Inicialización
  // ---------------------------------------------------------------------------

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initAiAssistant);
  } else {
    initAiAssistant();
  }
})();
