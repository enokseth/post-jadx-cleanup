import os
import re
import json
from pathlib import Path
from tqdm import tqdm
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
from time import sleep
from pyvis.network import Network

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

def generate_interactive_html_graph(file_dependencies, output_path):
    console.print("[bold magenta]🌐 Génération du graphe interactif HTML...[/bold magenta]\n")
    
    html_graph = Network(height="900px", width="100%", bgcolor="#1e1e1e", font_color="white", directed=True)
    html_graph.barnes_hut()

    total_files = len(file_dependencies)
    
    # Utilisation de tqdm pour afficher la progression des fichiers traités
    with tqdm(total=total_files, desc="Traitement des fichiers", ncols=80) as pbar:
        for src_file, data in file_dependencies.items():
            html_graph.add_node(src_file, label=src_file, title=data['package'], shape='dot')
            for dep in data['dependencies']:
                html_graph.add_node(dep, label=dep, shape='dot')
                html_graph.add_edge(src_file, dep)
            
            # Mise à jour de la barre de progression après chaque fichier traité
            pbar.update(1)

    # Génération du fichier HTML final
    html_output = output_path / "graph_dependencies.html"
    html_graph.show(str(html_output))
    console.print(f"[green]📎 Fichier HTML généré :[/green] [bold cyan]{html_output}[/bold cyan]\n")


def main():
    os.system("clear")
    console.print(Panel.fit(ASCII_LOGO, title="🚀", subtitle="v1.1 with Interactive Graph"))

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

    generate_interactive_html_graph(file_dependencies, output_dir)

if __name__ == "__main__":
    main()
