def infer_type(name):
    return name.split("::")[0]  # take everything before '::'


def coloring_edges(graph):

    graph.vs["type"] = [infer_type(n) for n in graph.vs["name"]]
    # Define a mapping of types to colors
    type_to_color = {
        "Anatomy": "#F2C6A0",  # телесный / мягкий оранжево-бежевый
        "Atc": "#B3CDE3",  # аптечный голубой (табличный, стандартный)
        "Biological Process": "#A9E2C1",  # мятно-зелёный (жизненные процессы)
        "Cellular Component": "#D0B7E6",  # сиреневый (внутриклеточные структуры)
        "Compound": "#FFE066",  # насыщенно-жёлтый (таблетки, капсулы)
        "Disease": "#F67280",  # розово-красный (боль, воспаление)
        "Gene": "#72A1E5",  # синий (ассоциация с ДНК, наукой)
        "Molecular Function": "#B8A9C9",  # светлый фиолетовый (молекулярный масштаб)
        "Pathway": "#F6C667",  # янтарный (биохимические пути)
        "Pharmacologic Class": "#FFB347",  # тёплый апельсиновый (лекарственные группы)
        "Side Effect": "#B4E197",  # кислотно-зелёный (неприятные реакции)
        "Symptom": "#FFB7CE",  # бледно-розовый (ощущения, субъективность)
        "Tax": "#CFCFCF",  # нейтрально-серый (таксономия, классификация)
        "Other": "#999999",  # тёмно-серый (прочее/неизвестное)
    }
    # Apply the color mapping to the vertex colors
    graph.vs["color"] = [type_to_color.get(t, "gray") for t in graph.vs["type"]]
    # Set the edge color based on the source and target vertex types
    # graph.vs["label"] = [n.split("::")[-1] for n in graph.vs["name"]]
