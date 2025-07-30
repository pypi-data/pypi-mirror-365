import os
import urllib.request
import json
import subprocess
from colorama import init, Fore, Style

init(autoreset=True)

version_manifest_url = "https://piston-meta.mojang.com/mc/game/version_manifest.json"
selected_version = None
server_folder = None

def spausdinti_antraste(tekstas):
    print(Fore.CYAN + Style.BRIGHT + tekstas)

def spausdinti_info(tekstas):
    print(Fore.GREEN + tekstas)

def spausdinti_klaida(tekstas):
    print(Fore.RED + tekstas)

def spausdinti_komandas():
    print(Fore.YELLOW + "Galimos komandos:")
    print(Fore.YELLOW + " - mdc help")
    print(Fore.YELLOW + " - mdc --version")
    print(Fore.YELLOW + " - mdc * version")
    print(Fore.YELLOW + " - mdc launch")
    print(Fore.YELLOW + " - exit")

def gauti_versijas():
    with urllib.request.urlopen(version_manifest_url) as response:
        data = json.load(response)
        return data["versions"]

def parodyk_versijas(versions, kiek=20):
    spausdinti_antraste("Galimos Minecraft versijos (stabilios):")
    stabilios = [v for v in versions if v["type"] == "release"]
    for i, v in enumerate(stabilios[:kiek], 1):
        print(Fore.MAGENTA + f"[{i}] {v['id']}")
    return stabilios[:kiek]

def atsisiusti_server_jar(version_info):
    global selected_version, server_folder
    version_id = version_info["id"]
    selected_version = version_id
    spausdinti_info(f"Atsiunčiama Minecraft {version_id}...")

    try:
        with urllib.request.urlopen(version_info["url"]) as response:
            version_data = json.load(response)
            jar_url = version_data["downloads"]["server"]["url"]

        server_folder = f"minecraft_server_{version_id}"
        os.makedirs(server_folder, exist_ok=True)
        jar_path = os.path.join(server_folder, "server.jar")

        urllib.request.urlretrieve(jar_url, jar_path)
        with open(os.path.join(server_folder, "eula.txt"), "w") as f:
            f.write("eula=true")

        spausdinti_info(f"✅ Serveris {version_id} paruoštas!")
    except Exception as e:
        spausdinti_klaida(f"❌ Klaida atsisiunčiant serverį: {e}")

def pasirinkti_versija():
    try:
        versions = gauti_versijas()
        shown_versions = parodyk_versijas(versions, kiek=20)
        pasirinkimas = int(input(Fore.WHITE + Style.BRIGHT + "Pasirink versiją (numeris): "))
        if 1 <= pasirinkimas <= len(shown_versions):
            atsisiusti_server_jar(shown_versions[pasirinkimas - 1])
        else:
            spausdinti_klaida("❗ Netinkamas pasirinkimas.")
    except ValueError:
        spausdinti_klaida("❗ Įvesk tik skaičių.")
    except Exception as e:
        spausdinti_klaida(f"❗ Klaida: {e}")

def paleisti_serveri():
    if selected_version and server_folder:
        spausdinti_info(f"🟢 Paleidžiamas Minecraft serveris {selected_version}...")
        try:
            subprocess.run(["java", "-Xmx1024M", "-Xms1024M", "-jar", "server.jar", "nogui"], cwd=server_folder)
        except FileNotFoundError:
            spausdinti_klaida("❌ Java nerasta. Įdiek Java ir pridėk į PATH.")
    else:
        spausdinti_klaida("❗ Pirma pasirink versiją su komanda: mdc * version")

def main():
    spausdinti_antraste("Matas Račkauskas console custom made VERSION 0.1")
    while True:
        try:
            cmd = input(Fore.WHITE + Style.BRIGHT + "~ € ").strip()
            if cmd == "mdc help":
                spausdinti_komandas()
            elif cmd in ["mdc --version", "mdc -v"]:
                print(Fore.CYAN + "MDC versija 0.1")
            elif cmd == "mdc * version":
                pasirinkti_versija()
            elif cmd == "mdc launch":
                paleisti_serveri()
            elif cmd == "exit":
                print(Fore.GREEN + "👋 Iki!")
                break
            else:
                spausdinti_klaida("Nežinoma komanda. Naudok: mdc help")
        except KeyboardInterrupt:
            print("\n" + Fore.YELLOW + "⛔ Išeinama iš programos.")
            break

if __name__ == "__main__":
    main()
