import flet as ft
import csv
import os
import asyncio

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
                preco_raw = linha.get("Preco", "").strip().replace(",", ".")
                preco = float(preco_raw)
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
# APP
# =========================
async def main(page: ft.Page):
    page.title = "🛒 Mínimos Preços - Sergipe"
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO
    page.bgcolor = ft.Colors.WHITE

    dados = carregar_dados()

    # =========================
    # TABELA
    # =========================
    tabela = ft.DataTable(
        columns=[
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
            tabela.rows.append(
                ft.DataRow(
                    cells=[
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
        contador.value = f"{len(filtrado)} resultados encontrados" if filtrado else "Nenhum produto encontrado"
        atualizar_tabela(filtrado)

    busca = ft.TextField(label="Buscar produto", prefix_icon=ft.Icons.SEARCH, expand=True, on_change=buscar)
    cidade_input = ft.TextField(label="Cidade", value="Aracaju", width=200, on_change=buscar)
    estado_input = ft.TextField(label="Estado", value="SE", width=120, on_change=buscar)

    atualizar_tabela(dados)

    # =========================
    # TOPO
    # =========================
    titulo = ft.Text("📊 Comparador de Preços", size=22, weight=ft.FontWeight.BOLD)
    contador = ft.Text("", italic=True, color=ft.Colors.GREY)
    filtros = ft.Row([busca, cidade_input, estado_input])

    # =========================
    # LOGO PRINCIPAL
    # =========================
    logo = ft.Image(src="logo.png", width=380, fit="contain")  # coloque a logo em assets/

    # =========================
    # CARROSSEL (via assets/)
    # =========================
    carousel_imgs = [
        "carousel/img.png",
        "carousel/img_1.png",
        "carousel/img_2.png",
    ]  # todas dentro da pasta assets/
    carousel_index = 0
    carousel_image = ft.Image(src=carousel_imgs[carousel_index], width=380, height=250, fit="contain")

    async def loop_carrossel():
        nonlocal carousel_index
        while True:
            await asyncio.sleep(10)
            carousel_index = (carousel_index + 1) % len(carousel_imgs)
            carousel_image.src = carousel_imgs[carousel_index]
            page.update()

    # =========================
    # LAYOUT RESPONSIVO
    # =========================
    def montar_layout():
        if page.width < 800:
            return ft.Column([
                ft.Container(content=logo, padding=10, alignment=ft.Alignment.CENTER),
                ft.Container(content=carousel_image, padding=10, alignment=ft.Alignment.CENTER),
                ft.Container(content=tabela, padding=10)
            ])
        else:
            return ft.Row([
                ft.Container(content=tabela, expand=True, padding=15),
                ft.Container(
                    content=ft.Column([logo, ft.Container(height=10), carousel_image], alignment=ft.MainAxisAlignment.START),
                    width=420,
                    padding=15
                )
            ], vertical_alignment=ft.CrossAxisAlignment.START)

    conteudo = montar_layout()
    page.add(titulo, filtros, contador, ft.Divider(), conteudo)

    # =========================
    # INICIAR CARROSSEL
    # =========================
    asyncio.create_task(loop_carrossel())

# =========================
# EXECUÇÃO (RENDER)
# =========================
ft.run(main, host="0.0.0.0", port=10000, assets_dir="assets")  # ⚠️ assets_dir necessário
