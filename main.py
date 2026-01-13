import flet as ft
import csv
import os
import asyncio
import base64
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

ARQUIVO = "precos.csv"

# =========================
# CARREGAR DADOS
# =========================
def carregar_dados():
    dados = []
    if not os.path.exists(ARQUIVO):
        return dados

    with open(ARQUIVO, encoding="utf-8", newline="") as f:
        leitor = csv.DictReader(f)
        for linha in leitor:
            try:
                preco = float(linha.get("Preco", "").replace(",", "."))
                dados.append({
                    "Produto": linha.get("Produto", ""),
                    "Marca": linha.get("Marca", ""),
                    "Unidade": linha.get("Unidade", ""),
                    "Preco": preco,
                    "Local": linha.get("Local", ""),
                    "Cidade": linha.get("Cidade", ""),
                    "Estado": linha.get("Estado", ""),
                })
            except ValueError:
                continue
    return dados

# =========================
# GERAR PDF EM MEMÓRIA
# =========================
def gerar_pdf_base64(itens):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    largura, altura = A4

    y = altura - 40
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, "Lista de Compras - Mínimo Preço")
    y -= 30

    c.setFont("Helvetica", 10)

    for item in itens:
        texto = (
            f"{item['Produto']} | {item['Marca']} | "
            f"{item['Unidade']} | R$ {item['Preco']:.2f} | {item['Local']}"
        )
        c.drawString(40, y, texto)
        y -= 15
        if y < 40:
            c.showPage()
            y = altura - 40

    c.save()
    buffer.seek(0)

    pdf_bytes = buffer.read()
    return base64.b64encode(pdf_bytes).decode("utf-8")

# =========================
# APP
# =========================
async def main(page: ft.Page):
    page.title = "Mínimo Preço - Sergipe"
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO
    page.bgcolor = ft.Colors.BLACK

    dados = carregar_dados()
    selecionados = []

    # =========================
    # TABELA
    # =========================
    tabela = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("✔")),
            ft.DataColumn(ft.Text("Produto")),
            ft.DataColumn(ft.Text("Marca")),
            ft.DataColumn(ft.Text("Unidade")),
            ft.DataColumn(ft.Text("Preço")),
            ft.DataColumn(ft.Text("Local")),
            ft.DataColumn(ft.Text("Cidade")),
            ft.DataColumn(ft.Text("Estado")),
        ],
        rows=[]
    )

    def atualizar_tabela(lista):
        tabela.rows.clear()
        for item in lista:
            def marcar(e, i=item):
                if e.control.value and i not in selecionados:
                    selecionados.append(i)
                elif not e.control.value and i in selecionados:
                    selecionados.remove(i)

            tabela.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Checkbox(on_change=marcar)),
                        ft.DataCell(ft.Text(item["Produto"])),
                        ft.DataCell(ft.Text(item["Marca"])),
                        ft.DataCell(ft.Text(item["Unidade"])),
                        ft.DataCell(ft.Text(f"R$ {item['Preco']:.2f}")),
                        ft.DataCell(ft.Text(item["Local"])),
                        ft.DataCell(ft.Text(item["Cidade"])),
                        ft.DataCell(ft.Text(item["Estado"])),
                    ]
                )
            )
        page.update()

    # =========================
    # BUSCA
    # =========================
    def buscar(e):
        termo = busca.value.lower()
        cidade = cidade_input.value.lower()
        estado = estado_input.value.lower()

        filtrado = [
            d for d in dados
            if termo in d["Produto"].lower()
            and cidade in d["Cidade"].lower()
            and estado in d["Estado"].lower()
        ]

        filtrado.sort(key=lambda x: x["Preco"])
        contador.value = f"{len(filtrado)} resultados encontrados"
        atualizar_tabela(filtrado)

    busca = ft.TextField(label="Buscar produto", expand=True, on_change=buscar)
    cidade_input = ft.TextField(label="Cidade", value="Aracaju", width=200, on_change=buscar)
    estado_input = ft.TextField(label="Estado", value="SE", width=120, on_change=buscar)

    atualizar_tabela(dados)

    # =========================
    # GERAR PDF (WEB SAFE)
    # =========================
    async def gerar_lista(e):
        if not selecionados:
            page.snack_bar = ft.SnackBar(ft.Text("Selecione ao menos um item"))
            page.snack_bar.open = True
            page.update()
            return

        pdf_b64 = gerar_pdf_base64(selecionados)
        nome = f"lista_compras_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

        download_url = (
            f"data:application/pdf;base64,{pdf_b64}"
        )

        page.open(
            ft.WindowOpenEvent(
                url=download_url,
                window_name=nome
            )
        )

    botao_pdf = ft.Button(
        content=ft.Row(
            [ft.Icon(ft.Icons.PICTURE_AS_PDF), ft.Text("Gerar lista em PDF")],
            alignment=ft.MainAxisAlignment.CENTER
        ),
        on_click=gerar_lista
    )

    titulo = ft.Text("Comparador de Preços", size=22, weight=ft.FontWeight.BOLD)
    contador = ft.Text("", italic=True, color=ft.Colors.GREY)
    filtros = ft.Row([busca, cidade_input, estado_input, botao_pdf])

    logo = ft.Image(src="logo.png", width=380)
    carousel = ft.Image(src="img_1.png", width=380, height=250)

    topo_visual = ft.Row(
        [logo, carousel],
        alignment=ft.MainAxisAlignment.CENTER
    )

    page.add(
        topo_visual,
        ft.Divider(),
        titulo,
        filtros,
        contador,
        ft.Divider(),
        tabela
    )

# =========================
# EXECUÇÃO
# =========================
ft.run(
    main,
    host="0.0.0.0",
    port=10000,
    assets_dir="assets"
)
