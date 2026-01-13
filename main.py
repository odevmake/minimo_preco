import flet as ft
import csv
import os
import asyncio
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from flet import UrlLauncher

ARQUIVO = "precos.csv"
ASSETS_DIR = "assets"

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
# GERAR PDF
# =========================
def gerar_pdf(itens):
    nome_pdf = f"lista_compras_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    caminho_pdf = os.path.join(ASSETS_DIR, nome_pdf)

    c = canvas.Canvas(caminho_pdf, pagesize=A4)
    largura, altura = A4

    y = altura - 40
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, "Lista de Compras - Mínimo Preço")
    y -= 30

    c.setFont("Helvetica", 10)

    for item in itens:
        texto = f"{item['Produto']} | {item['Marca']} | {item['Unidade']} | R$ {item['Preco']:.2f} | {item['Local']}"
        c.drawString(40, y, texto)
        y -= 15
        if y < 40:
            c.showPage()
            y = altura - 40

    c.save()
    return nome_pdf

# =========================
# APP
# =========================
async def main(page: ft.Page):
    page.title = "🛒 Mínimo Preço - Sergipe"
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
    # GERAR PDF
    # =========================
    async def gerar_lista(e):
        if not selecionados:
            page.snack_bar = ft.SnackBar(ft.Text("Selecione ao menos um item"))
            page.snack_bar.open = True
            page.update()
            return

        nome_pdf = gerar_pdf(selecionados)
        launcher = UrlLauncher()

        if page.web:
            await launcher.launch_url(f"/assets/{nome_pdf}")
        else:
            caminho = os.path.abspath(os.path.join(ASSETS_DIR, nome_pdf))
            await launcher.launch_url(f"file:///{caminho}")

    botao_pdf = ft.Button(
        content=ft.Row(
            [ft.Icon(ft.Icons.PICTURE_AS_PDF), ft.Text("Gerar lista em PDF")],
            alignment=ft.MainAxisAlignment.CENTER
        ),
        on_click=gerar_lista
    )

    # =========================
    # TOPO
    # =========================
    titulo = ft.Text("Comparador de Preços", size=22, weight=ft.FontWeight.BOLD)
    contador = ft.Text("", italic=True, color=ft.Colors.GREY)
    filtros = ft.Row([busca, cidade_input, estado_input, botao_pdf])

    # =========================
    # LOGO + CARROSSEL (TOPO)
    # =========================
    logo = ft.Image(src="logo.png", width=380)
    carousel_imgs = ["img_1.png", "img_2.png", "img_3.png"]
    carousel_index = 0
    carousel = ft.Image(src=carousel_imgs[0], width=380, height=250)

    async def loop_carrossel():
        nonlocal carousel_index
        while page.session:
            await asyncio.sleep(10)
            carousel_index = (carousel_index + 1) % len(carousel_imgs)
            carousel.src = carousel_imgs[carousel_index]
            page.update()

    topo_visual = ft.Row(
        [logo, carousel],
        alignment=ft.MainAxisAlignment.CENTER,
        #horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    # =========================
    # LAYOUT PRINCIPAL
    # =========================
    page.add(
        topo_visual,
        ft.Divider(),
        titulo,
        filtros,
        contador,
        ft.Divider(),
        tabela
    )

    asyncio.create_task(loop_carrossel())

# =========================
# EXECUÇÃO
# =========================
ft.run(
    main,
    host="0.0.0.0",
    port=10000,
    assets_dir="assets"
)
