import os
import pandas as pd
import re

def merge_counts():
    """
    Fusionne tous les fichiers de type scenarios_table_H37Rv_XXX_mask.tsv
    en un seul fichier CSV combiné sur la colonne 'Scenario'.
    """
    pattern = r"scenarios_table_H37Rv_(.+)_mask\.tsv"
    files = [f for f in os.listdir('.') if re.search(pattern, f)]

    if not files:
        print("❌ Aucun fichier de scénarios trouvé à fusionner.")
        return

    merged_df = None
    for file in files:
        match = re.search(pattern, file)
        if not match:
            continue
        sample = match.group(1)
        df = pd.read_csv(file, sep='\t', usecols=["Scenario", "Count"])
        df.rename(columns={"Count": sample}, inplace=True)

        if merged_df is None:
            merged_df = df
        else:
            merged_df = pd.merge(merged_df, df, on="Scenario", how="outer")

    if merged_df is not None:
        output_file = "combined_scenarios_counts1.csv"
        merged_df.to_csv(output_file, index=False)
        print(f"✅ Fichier fusionné sauvegardé : {output_file}")
    else:
        print("❌ Aucune donnée valide à fusionner.")
