import os
import subprocess
import sys
import importlib.util

# --- 1. Liste des bibliothèques nécessaires ---
required_packages = {
    "streamlit": "streamlit",
    "pandas": "pandas",
    "numpy": "numpy",
    "plotly": "plotly",
    "folium": "folium",
    "streamlit_folium": "streamlit-folium",
    "wordcloud": "wordcloud",
    "matplotlib": "matplotlib",
    "networkx": "networkx"
}

# --- 2. Vérification et installation si manquant ---
print("🔍 Vérification des bibliothèques Python...")
for module_name, pip_name in required_packages.items():
    if importlib.util.find_spec(module_name) is None:
        print(f"📦 Installation de : {pip_name}")
        subprocess.run([sys.executable, "-m", "pip", "install", pip_name])

print("✅ Toutes les dépendances sont installées.")

# --- 3. Lancer l'application Streamlit ---
try:
    version=input("V1 ou V2 (1,2)")
    if version=="2":
        os.chdir("code2")
        print("🚀 Lancement de Streamlit : menu.py")
        subprocess.run(["streamlit", "run", "menu.py"])
    else:
        os.chdir("code")
        print("🚀 Lancement de Streamlit : menu.py")
        subprocess.run(["streamlit", "run", "menu.py"])
except Exception as e:
    print(f"❌ Erreur pendant le lancement : {e}")
