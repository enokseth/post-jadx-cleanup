import os
import re
import json
from pathlib import Path
from tqdm import tqdm
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from time import sleep
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

console = Console()

ASCII_LOGO = r"""
 ██████╗██╗  ██╗██╗███╗   ███╗███████╗██████╗  █████╗     ██╗   ██╗███████╗██████╗ ███████╗
██╔════╝██║  ██║██║████╗ ████║██╔════╝██╔══██╗██╔══██╗    ██║   ██║██╔════╝██╔══██╗██╔════╝
██║     ███████║██║██╔████╔██║█████╗  ██████╔╝███████║    ██║   ██║█████╗  ██████╔╝█████╗  
██║     ██╔══██║██║██║╚██╔╝██║██╔══╝  ██╔═══╝ ██╔══██║    ╚██╗ ██╔╝██╔══╝  ██╔══██╗██╔══╝  
╚██████╗██║  ██║██║██║ ╚═╝ ██║███████╗██║     ██║  ██║     ╚████╔╝ ███████╗██║  ██║███████╗
 ╚═════╝╚═╝  ╚═╝╚═╝╚═╝     ╚═╝╚══════╝╚═╝     ╚═╝  ╚═╝      ╚═══╝  ╚══════╝╚═╝  ╚═╝╚══════╝
                        Obfuscated Java Static Analyzer - By Omega Gsm
"""

# Regex
re_package = re.compile(r'^\s*package\s+([\w.]+);')
re_import = re.compile(r'^\s*import\s+([\w.]+);')
re_new = re.compile(r'new\s+([A-Z]\w*)')
re_extends = re.compile(r'extends\s+([A-Z]\w*)')
re_implements = re.compile(r'implements\s+([\w\s,]+)')

def extract_package_and_deps(java_file):
    deps = set()
    pkg = ""
    try:
        with open(java_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            content = ''.join(lines)

            for line in lines:
                if (match := re_package.match(line)):
                    pkg = match.group(1)
                    break

            deps.update(re_import.findall(content))
            deps.update(re_new.findall(content))
            deps.update(re_extends.findall(content))
            impls = re_implements.findall(content)
            for group in impls:
                deps.update(map(str.strip, group.split(",")))
    except Exception as e:
        console.print(f"[red]Erreur lecture fichier : {java_file} - {e}[/red]")

    return pkg, deps

def generate_dependency_graph(file_dependencies, output_path):
    console.print("\n[bold magenta]🧠 Génération du graphe des dépendances...[/bold magenta]\n")
    G = nx.DiGraph()

    for src_file, data in file_dependencies.items():
        src_node = src_file
        for dep in data['dependencies']:
            G.add_edge(src_node, dep)

    plt.figure(figsize=(18, 12))
    pos = nx.spring_layout(G, k=0.5, iterations=50)
    nx.draw_networkx_nodes(G, pos, node_size=800, node_color="skyblue", edgecolors="black")
    nx.draw_networkx_edges(G, pos, arrowstyle='->', arrowsize=20)
    nx.draw_networkx_labels(G, pos, font_size=9, font_family="monospace")

    img_path = output_path / "graph_dependencies.png"
    plt.title("Java Dependency Graph")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(img_path, dpi=300)
    plt.close()

    console.print(f"[green]📌 Graphe enregistré :[/green] [bold cyan]{img_path}[/bold cyan]\n")

def main():
    os.system("clear")
    console.print(Panel.fit(ASCII_LOGO, title="🚀", subtitle="v1.1 with Graph"))

    source_path = Prompt.ask("\n📁 Entrez le chemin du dossier contenant les .java", default="./app/src/main/java")
    SOURCE_ROOT = Path(source_path).resolve()

    if not SOURCE_ROOT.exists():
        console.print(f"[red]❌ Dossier non trouvé : {SOURCE_ROOT}[/red]")
        return

    java_files = list(SOURCE_ROOT.rglob("*.java"))
    console.print(f"\n[cyan]🔍 {len(java_files)} fichiers Java détectés dans {SOURCE_ROOT}[/cyan]\n")

    file_dependencies = {}

    console.print("[bold yellow]📂 Indexation des classes et dépendances...[/bold yellow]\n")
    sleep(0.5)

    for java_file in tqdm(java_files, desc="Analyse des fichiers", ncols=80):
        pkg, deps = extract_package_and_deps(java_file)
        rel_path = str(java_file.relative_to(SOURCE_ROOT))
        file_dependencies[rel_path] = {
            "package": pkg,
            "dependencies": sorted(list(deps))
        }

    output_dir = Path("chimera_vertex_mapping")
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "resultat.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(file_dependencies, f, indent=2)

    console.print("\n[green bold]✅ Analyse terminée ![/green bold]")
    console.print(f"📝 Résultat enregistré dans : [bold cyan]{output_file}[/bold cyan]\n")

    # Générer graphe
    generate_dependency_graph(file_dependencies, output_dir)

if __name__ == "__main__":
    main()
