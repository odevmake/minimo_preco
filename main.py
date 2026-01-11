import flet as ft
import csv
import os

ARQUIVO = "precos.csv"


# =========================
# CARREGAR DADOS COM SEGURANÇA
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
                continue  # ignora linha quebrada

    return dados


# =========================
# APP
# =========================
def main(page: ft.Page):
    page.title = "🛒 Melhores Preços - Sergipe"
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

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

    busca = ft.TextField(
        label="Buscar produto",
        prefix_icon=ft.Icons.SEARCH,
        expand=True,
        on_change=buscar
    )

    cidade_input = ft.TextField(
        label="Cidade",
        value="Aracaju",
        width=200,
        on_change=buscar
    )

    estado_input = ft.TextField(
        label="Estado",
        value="SE",
        width=120,
        on_change=buscar
    )

    atualizar_tabela(dados)

    # =========================
    # TOPO
    # =========================
    titulo = ft.Text(
        "📊 Comparador de Preços",
        size=22,
        weight=ft.FontWeight.BOLD
    )

    contador = ft.Text(

        "",
        italic=True,
        color=ft.Colors.GREY

    )

    filtros = ft.Row([
        busca,
        cidade_input,
        estado_input
    ])

    # =========================
    # IMAGEM (RENDER OK)
    # =========================
    logo = ft.Image(
        src="img.png",  # ⚠️ SEM assets/
        width=380,
        fit="contain"
    )

    def montar_layout():
        # layout para celular
        if page.width < 800:
            return ft.Column(
                [
                    ft.Container(
                        content=logo,
                        padding=10,
                        alignment=ft.Alignment.CENTER
                    ),
                    ft.Container(
                        content=tabela,
                        padding=10
                    )
                ]
            )

        # layout para PC
        return ft.Row(
            [
                ft.Container(
                    content=tabela,
                    expand=True,
                    padding=15
                ),
                ft.Container(
                    content=ft.Column(
                        [logo],
                        alignment=ft.MainAxisAlignment.START
                    ),
                    width=420,
                    padding=15
                )
            ],
            vertical_alignment=ft.CrossAxisAlignment.START
        )

    # =========================
    # LAYOUT PRINCIPAL
    # =========================
    conteudo = montar_layout()
    page.add(
        titulo,
        filtros,
        contador,
        ft.Divider(),
        conteudo
    )


# =========================
# EXECUÇÃO (RENDER)
# =========================
ft.app(
    target=main,
    #assets_dir="assets",
    host="0.0.0.0",
    port=10000
)
