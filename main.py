import flet as ft
import csv
import os

ARQUIVO = "precos.csv"


def carregar_dados():
    dados = []

    # Proteção para erro de arquivo
    if not os.path.exists(ARQUIVO):
        return dados

    with open(ARQUIVO, encoding="utf-8") as f:
        leitor = csv.DictReader(f)
        for linha in leitor:
            linha["Preco"] = float(linha["Preco"])
            dados.append(linha)
    return dados


def main(page: ft.Page):
    page.title = "🛒 Melhores Preços - Sergipe"
    page.padding = 20

    dados = carregar_dados()

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

    page.add(
        ft.Text("📊 Comparador de Preços", size=22, weight=ft.FontWeight.BOLD),
        ft.Row([busca, cidade_input, estado_input]),
        ft.Divider(),
        tabela
    )


# 🔴 ISSO É O QUE FAZ FUNCIONAR NO RENDER
ft.app(
    target=main,
    view=ft.WEB_BROWSER,
    host="0.0.0.0",
    port=10000
)
