# 🧬 SGLab-tools

[![PyPI version](https://img.shields.io/pypi/v/SGLab-tools.svg?color=blue&logo=python&label=PyPI)](https://pypi.org/project/SGLab-tools/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.8+-brightgreen.svg)](https://www.python.org/)
[![GitHub](https://img.shields.io/badge/source-GitHub-black?logo=github)](https://github.com/EtienneNtumba/SGLab-tools)

---

## 🧠 Description

**SGLab-tools** est un outil modulaire et reproductible pour l’analyse comparative de génomes, conçu pour détecter et classifier les différences nucléotidiques entre des génomes de souches bactériennes ou autres organismes. Il permet l’alignement, l’extraction de différences, le masquage de régions non fiables, le comptage de scénarios évolutifs, et la génération de visualisations.

> Développé par **Etienne Ntumba Kabongo**  
> Sous la supervision de **Pr. Simon Grandjean Lapierre** (Université de Montréal) et **Pr. Martin Smith** (Université de Montréal)  
> Laboratoires de bioinformatique et de génomique, Université de Montréal et McGill

---

## 🧰 Fonctionnalités

- 🔁 Alignement pair-à-pair de génomes avec `minimap2`
- 🧬 Extraction de différences (SNPs, gaps, insertions, N)
- 🛡️ Masquage de régions peu fiables avec des fichiers BED
- 📊 Comptage des scénarios de variation (8 scénarios types)
- 📁 Fusion automatique de résultats multi-souches
- 📈 Génération de visualisations (barplot, heatmap)
- 📤 Export en `.csv`, `.tsv`, `.xlsx` enrichi avec `Description` et `Total`
- ⚡ Interface en ligne de commande simple (`sglab`)

---

## 📦 Installation

Depuis [PyPI](https://pypi.org/project/SGLab-tools/) :

```bash
pip install SGLab-tools

```
Ou depuis le dépôt GitHub :

git clone https://github.com/EtienneNtumba/SGLab-tools.git
cd SGLab-tools
pip install .

Dépendances :

    Python ≥ 3.8

    Outils externes : minimap2

    Bibliothèques Python : typer, pandas, biopython, matplotlib, seaborn, openpyxl

📂 Exemple d'utilisation
1. Préparer un fichier sample.txt :

Ref     L_x
H37Rv   L1
H37Rv   L2
H37Rv   L5

Ce fichier indique quelles paires de génomes comparer.

Les fichiers suivants doivent être présents :

H37Rv.fasta, L1.fasta, L2.fasta, ...
H37Rv.bed, L1.bed, L2.bed, ...

2. Lancer le pipeline complet :

sglab run sample.txt

Cela génère pour chaque paire :

    un alignement .paf

    une table de différences .tsv

    un fichier masqué .tsv

    un comptage des scénarios

Puis fusionne tous les résultats en :

combined_scenarios_counts1.csv

3. Enrichir, exporter et visualiser :

sglab plot

Cela produit :

    combined_scenarios_augmented.csv / .tsv / .xlsx

    scenarios_barplot.png

    scenarios_heatmap.png

📊 Scénarios détectés
Code	Scénario	Description
1️⃣	N/N	N et N identiques
2️⃣	base/gap	Base (A/C/G/T) alignée sur gap
3️⃣	base/base	Base alignée sur base
4️⃣	gap/N	Gap aligné sur N
5️⃣	gap/base	Gap aligné sur base
6️⃣	N/base	N aligné sur base
7️⃣	base/N	Base alignée sur N
8️⃣	N/gap	N aligné sur gap
📁 Résultats générés

alignments_H37Rv_L1.paf
tables_H37Rv_L1.tsv
tables_H37Rv_L1_mask.tsv
scenarios_table_H37Rv_L1_mask.tsv
combined_scenarios_counts1.csv
combined_scenarios_augmented.{csv,tsv,xlsx}
scenarios_barplot.png
scenarios_heatmap.png

💡 Commandes CLI disponibles

sglab run sample.txt            # Pipeline complet
sglab mask --input A.tsv --ref A.bed --query B.bed
sglab count --input fichier.tsv
sglab merge                     # Fusion des scénarios
sglab plot                      # Enrichissement + visualisation

📜 Licence

Ce projet est distribué sous licence MIT.
🙏 Remerciements

Ce travail a été réalisé dans le cadre d’une recherche en génomique comparative de Mycobacterium tuberculosis, au sein du laboratoire du Pr. Simon Grandjean Lapierre et du Pr. Martin Smith, avec l’objectif d’outiller l’analyse reproductible des génomes bactériens.
🔗 Liens utiles

    GitHub Repository

    Page PyPI

    minimap2

    Biopython

    Typer CLI
