import cv2
from pyzbar import pyzbar
from tkinter import messagebox
# Importa as funções de busca por produto (ID e Cód. Barras)
from produto import buscar_produto_por_id, buscar_produto_por_codigo_barras 

def abrir_camera_codigo_barras():
    """
    Abre a webcam e tenta ler um código de barras.
    """
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("Erro de Câmera", "Não foi possível acessar a câmera.")
            return None

        messagebox.showinfo("Leitor de Câmera", "Aproxime o código de barras da câmera.\nPressione 'Q' para sair.")

        codigo_detectado = None

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            barcodes = pyzbar.decode(frame)
            for barcode in barcodes:
                codigo_detectado = barcode.data.decode("utf-8")
                (x, y, w, h) = barcode.rect
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, codigo_detectado, (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                cap.release()
                cv2.destroyAllWindows()
                messagebox.showinfo("Código Detectado", f"Código lido: {codigo_detectado}")
                return codigo_detectado

            cv2.imshow("Leitor de Código de Barras - Pressione Q para sair", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()

        if not codigo_detectado:
            messagebox.showwarning("Leitura Cancelada", "Nenhum código foi detectado.")
        return codigo_detectado

    except Exception as e:
        try:
            cap.release()
            cv2.destroyAllWindows()
        except:
            pass
        messagebox.showerror("Erro", f"Erro ao acessar a câmera: {e}")
        return None


def processar_codigo_barras(entry_widget, label_status=None):
    """
    Busca o produto pelo ID (se for numérico curto) ou pelo Código de Barras (string).
    Se encontrado, preenche o campo de entrada com o ID do produto para permitir a movimentação.
    """
    codigo = entry_widget.get().strip()
    produto = None

    if not codigo:
        if label_status:
            label_status.configure(text="Nenhum código informado.", text_color="#E67E22")
        return None

    # Tenta buscar por ID se o código for numérico e for um ID plausível (ex: até 9 dígitos)
    if codigo.isdigit() and len(codigo) < 10:
        produto = buscar_produto_por_id(int(codigo))

    # Se não encontrou por ID ou se o código é longo (provavelmente código de barras)
    if not produto:
        produto = buscar_produto_por_codigo_barras(codigo)


    if produto:
        # CORREÇÃO CRÍTICA: Desempacota 6 campos do produto.
        # id_prod, nome, categoria, preco, qtd, codigo_barras (6 campos)
        id_prod, nome, categoria, preco, qtd, codigo_barras = produto
        
        # O campo de entrada DEVE conter o ID do produto para que a função registrar_movimentacao funcione.
        entry_widget.delete(0, 'end')
        entry_widget.insert(0, str(id_prod))

        if label_status:
            label_status.configure(text=f"Produto: {nome} (Estoque: {qtd})", text_color="#2ECC71")
        return produto
    else:
        if label_status:
            label_status.configure(text="Produto não encontrado!", text_color="#E74C3C")
        # Se não encontrou, limpa o campo de entrada para evitar erros de casting.
        entry_widget.delete(0, 'end')
        return None