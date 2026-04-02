import { Editor } from "@tiptap/core";
import StarterKit from "@tiptap/starter-kit";
import Underline from "@tiptap/extension-underline";
import Link from "@tiptap/extension-link";
import Image from "@tiptap/extension-image";
import Table from "@tiptap/extension-table";
import TableRow from "@tiptap/extension-table-row";
import TableCell from "@tiptap/extension-table-cell";
import TableHeader from "@tiptap/extension-table-header";
import Placeholder from "@tiptap/extension-placeholder";

/**
 * Definición de botones del toolbar.
 * Cada entrada describe un botón: etiqueta, tooltip, acción sobre el editor
 * y función para detectar si está activo (para resaltado visual).
 */
const TOOLBAR_BUTTONS = [
  {
    label: "H2",
    title: "Encabezado 2",
    action: (editor) => editor.chain().focus().toggleHeading({ level: 2 }).run(),
    isActive: (editor) => editor.isActive("heading", { level: 2 }),
  },
  {
    label: "H3",
    title: "Encabezado 3",
    action: (editor) => editor.chain().focus().toggleHeading({ level: 3 }).run(),
    isActive: (editor) => editor.isActive("heading", { level: 3 }),
  },
  {
    label: "H4",
    title: "Encabezado 4",
    action: (editor) => editor.chain().focus().toggleHeading({ level: 4 }).run(),
    isActive: (editor) => editor.isActive("heading", { level: 4 }),
  },
  { type: "separator" },
  {
    label: "N",
    title: "Negrita",
    action: (editor) => editor.chain().focus().toggleBold().run(),
    isActive: (editor) => editor.isActive("bold"),
    style: "font-weight:bold",
  },
  {
    label: "I",
    title: "Cursiva",
    action: (editor) => editor.chain().focus().toggleItalic().run(),
    isActive: (editor) => editor.isActive("italic"),
    style: "font-style:italic",
  },
  {
    label: "S",
    title: "Subrayado",
    action: (editor) => editor.chain().focus().toggleUnderline().run(),
    isActive: (editor) => editor.isActive("underline"),
    style: "text-decoration:underline",
  },
  { type: "separator" },
  {
    label: "• Lista",
    title: "Lista con viñetas",
    action: (editor) => editor.chain().focus().toggleBulletList().run(),
    isActive: (editor) => editor.isActive("bulletList"),
  },
  {
    label: "1. Lista",
    title: "Lista numerada",
    action: (editor) => editor.chain().focus().toggleOrderedList().run(),
    isActive: (editor) => editor.isActive("orderedList"),
  },
  { type: "separator" },
  {
    label: "❝",
    title: "Cita / Blockquote",
    action: (editor) => editor.chain().focus().toggleBlockquote().run(),
    isActive: (editor) => editor.isActive("blockquote"),
  },
  {
    label: "</>",
    title: "Código",
    action: (editor) => editor.chain().focus().toggleCode().run(),
    isActive: (editor) => editor.isActive("code"),
  },
  { type: "separator" },
  {
    label: "Enlace",
    title: "Insertar / editar enlace",
    action: (editor) => {
      const previousUrl = editor.getAttributes("link").href || "";
      const url = window.prompt("URL del enlace:", previousUrl);
      if (url === null) return; // cancelado
      if (url === "") {
        editor.chain().focus().extendMarkRange("link").unsetLink().run();
      } else {
        editor
          .chain()
          .focus()
          .extendMarkRange("link")
          .setLink({ href: url, target: "_blank" })
          .run();
      }
    },
    isActive: (editor) => editor.isActive("link"),
  },
  {
    label: "Imagen",
    title: "Insertar imagen por URL",
    action: (editor) => {
      const url = window.prompt("URL de la imagen:");
      if (!url) return;
      const alt = window.prompt("Texto alternativo (alt):", "");
      editor.chain().focus().setImage({ src: url, alt: alt || "" }).run();
    },
    isActive: () => false,
  },
  {
    label: "Tabla",
    title: "Insertar tabla 3×3",
    action: (editor) =>
      editor
        .chain()
        .focus()
        .insertTable({ rows: 3, cols: 3, withHeaderRow: true })
        .run(),
    isActive: (editor) => editor.isActive("table"),
  },
];

/**
 * Crea el elemento toolbar para un editor dado.
 * Se llama cada vez que el estado del editor cambia para actualizar
 * la clase "is-active" de cada botón.
 */
function buildToolbar(editor) {
  const toolbar = document.createElement("div");
  toolbar.className = "tiptap-toolbar";
  toolbar.setAttribute("role", "toolbar");
  toolbar.setAttribute("aria-label", "Barra de herramientas del editor");

  TOOLBAR_BUTTONS.forEach((btn) => {
    if (btn.type === "separator") {
      const sep = document.createElement("span");
      sep.className = "tiptap-toolbar__separator";
      sep.setAttribute("aria-hidden", "true");
      toolbar.appendChild(sep);
      return;
    }

    const button = document.createElement("button");
    button.type = "button";
    button.textContent = btn.label;
    button.title = btn.title;
    button.setAttribute("aria-label", btn.title);
    if (btn.style) button.style.cssText = btn.style;

    button.addEventListener("click", (e) => {
      e.preventDefault();
      btn.action(editor);
    });

    // Guarda referencia para actualizar estado activo
    button._tiptapIsActive = btn.isActive;
    toolbar.appendChild(button);
  });

  return toolbar;
}

/**
 * Actualiza la clase "is-active" en todos los botones del toolbar.
 */
function syncToolbarState(toolbar, editor) {
  toolbar.querySelectorAll("button").forEach((btn) => {
    if (typeof btn._tiptapIsActive === "function") {
      btn.classList.toggle("is-active", btn._tiptapIsActive(editor));
    }
  });
}

/**
 * Inicializa un editor TipTap sobre un <textarea data-tiptap>.
 * El textarea queda oculto; se muestra el div `.tiptap-editor` en su lugar.
 * Al hacer submit del formulario, o en cada onUpdate, se sincroniza el HTML
 * de vuelta al textarea para que Django reciba el valor correcto.
 */
function initTiptapEditor(textarea) {
  // Contenedor externo
  const wrapper = document.createElement("div");
  wrapper.className = "tiptap-wrapper";
  textarea.parentNode.insertBefore(wrapper, textarea);

  // Ocultar textarea original
  textarea.style.display = "none";
  wrapper.appendChild(textarea);

  // Div donde TipTap monta su ProseMirror
  const editorEl = document.createElement("div");
  editorEl.className = "tiptap-editor";
  editorEl.setAttribute("aria-multiline", "true");
  editorEl.setAttribute("role", "textbox");
  editorEl.setAttribute("aria-label", textarea.getAttribute("aria-label") || "Editor de contenido");

  // Toolbar (se inserta antes del div del editor)
  const placeholderText =
    textarea.getAttribute("data-placeholder") || "Escribe el contenido aquí…";

  const editor = new Editor({
    element: editorEl,
    extensions: [
      StarterKit.configure({
        // Deshabilitar extensiones que se añaden por separado
        heading: { levels: [2, 3, 4] },
      }),
      Underline,
      Link.configure({
        openOnClick: false,
        HTMLAttributes: { rel: "noopener noreferrer" },
      }),
      Image.configure({ inline: false }),
      Table.configure({ resizable: false }),
      TableRow,
      TableCell,
      TableHeader,
      Placeholder.configure({ placeholder: placeholderText }),
    ],
    content: textarea.value || "",
    onUpdate({ editor }) {
      textarea.value = editor.getHTML();
    },
    onSelectionUpdate({ editor }) {
      syncToolbarState(toolbar, editor);
    },
    onTransaction({ editor }) {
      syncToolbarState(toolbar, editor);
    },
  });

  const toolbar = buildToolbar(editor);

  // Guardar referencia de la instancia en el elemento para acceso externo
  // (usado por el listener de 'tiptap:set-content' del asistente IA)
  editorEl._tiptapEditorInstance = editor;

  wrapper.appendChild(toolbar);
  wrapper.appendChild(editorEl);

  // Sincronizar al submit del formulario (por si acaso onUpdate no disparó)
  const form = textarea.closest("form");
  if (form) {
    form.addEventListener("submit", () => {
      textarea.value = editor.getHTML();
    });
  }

  return editor;
}

/**
 * Punto de entrada: inicializa todos los textareas marcados con data-tiptap.
 * Compatible con DOMContentLoaded y con scripts cargados de forma diferida.
 */
function initAllEditors() {
  document.querySelectorAll("textarea[data-tiptap]").forEach((textarea) => {
    // Evitar doble inicialización
    if (textarea.dataset.tiptapInitialized) return;
    textarea.dataset.tiptapInitialized = "true";
    initTiptapEditor(textarea);
  });
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initAllEditors);
} else {
  initAllEditors();
}

// Exponer para uso desde consola o scripts externos si se requiere
window.LogincoTiptap = { init: initAllEditors };

/**
 * Listener para el evento personalizado 'tiptap:set-content'.
 * Lo dispara el asistente IA (ai-assistant.js) cuando genera o mejora el body.
 * event.detail.content debe contener el HTML que se quiere cargar en el editor.
 *
 * Actualiza todos los editores TipTap inicializados en la página y también
 * sincroniza el valor del textarea oculto correspondiente.
 */
document.addEventListener("tiptap:set-content", function (event) {
  const newContent = (event.detail && event.detail.content) ? event.detail.content : "";

  // Buscar todos los textareas marcados como inicializados con TipTap
  document.querySelectorAll("textarea[data-tiptap-initialized]").forEach(function (textarea) {
    // El editor TipTap está montado sobre el hermano .tiptap-editor dentro del mismo .tiptap-wrapper
    const wrapper = textarea.closest(".tiptap-wrapper");
    if (!wrapper) return;

    const editorEl = wrapper.querySelector(".tiptap-editor");
    if (!editorEl) return;

    // Acceder a la instancia del editor expuesta por ProseMirror/TipTap
    // TipTap almacena la instancia en editorEl._tiptapEditor si la exponemos,
    // pero la forma más confiable es usar el objeto editor guardado en la instancia.
    // Usamos la referencia guardada en el elemento durante la inicialización.
    if (editorEl._tiptapEditorInstance) {
      editorEl._tiptapEditorInstance.commands.setContent(newContent, true);
      textarea.value = editorEl._tiptapEditorInstance.getHTML();
    } else {
      // Fallback: actualizar solo el textarea (TipTap lo leerá en el próximo sync)
      textarea.value = newContent;
    }
  });
});
