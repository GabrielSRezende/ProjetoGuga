def formatar_para_moeda(event):
    # Obter o widget associado ao evento
    entry_widget = event.widget
    # Remover símbolos antigos e formatar
    valor = entry_widget.get().replace("R$", "").replace(",", "").replace(".", "").strip()

    if valor.isdigit():  # Verificar se é número
        valor_formatado = f"R$ {int(valor):,}".replace(",", ".")
        entry_widget.delete(0, "end")
        entry_widget.insert(0, valor_formatado)



def remover_formatacao_monetaria(valor_formatado):
    """
    Remove a formatação de moeda de um valor formatado como 'R$ x.xxx,xx'.
    Exemplo: 'R$ 1.234,56' -> 1234.56
    """
    if not valor_formatado:
        return 0.0
    valor = valor_formatado.replace("R$", "").replace(".", "").replace(",", ".").strip()
    try:
        return float(valor)
    except ValueError:
        return 0.0

def atualizar_texto_checkbox(self):
    """Atualiza o texto do checkbox para 'Sim' ou 'Não'."""
    if self.possui_nota_var.get() == 1:
        self.entry_possui_nota.configure(text="Sim")
    else:
        self.entry_possui_nota.configure(text="Não")

