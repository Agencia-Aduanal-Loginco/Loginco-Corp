from django.forms import Textarea


class TiptapWidget(Textarea):
    """
    Widget que renderiza un <textarea> con el atributo ``data-tiptap``
    para que tiptap-bundle.js lo intercepte e inicialice el editor rico.

    El textarea queda oculto en el DOM; TipTap monta su propio div
    adyacente y sincroniza el HTML de vuelta al textarea en cada cambio
    y antes del submit del formulario.
    """

    def __init__(self, attrs=None):
        default_attrs = {"data-tiptap": "true", "rows": 20}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)
