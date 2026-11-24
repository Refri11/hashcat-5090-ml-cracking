#!/usr/bin/env python3
"""crack_agent.py — Orquestador: LLM local (Ollama/qwen3-coder) + hashcat (5090)."""
import argparse, json, re, subprocess, sys, urllib.request, urllib.error

OLLAMA_URL = "http://localhost:11435/api/chat"
MODEL = "qwen3-coder:30b"

CATALOG = {
    "ntlm": {
        "mode": 1000,
        "steps": {
            "dict":    {"desc": "Diccionario rockyou (train)",
                        "args": ["-a","0","{hashes}","train.txt"], "medido": "0%"},
            "best66":  {"desc": "train + best66 (90 reglas)",
                        "args": ["-a","0","{hashes}","train.txt","-r","/work/rules/best66.rule"], "medido": "32,47%"},
            "dive":    {"desc": "train + dive (~99k reglas)",
                        "args": ["-a","0","{hashes}","train.txt","-r","/opt/hashcat-8.0.0/rules/dive.rule"], "medido": "77,90%"},
            "pcfg":    {"desc": "PCFG entrenado (5e7 candidatos)",
                        "pipe": "python3 /work/pcfg_cracker/pcfg_guesser.py --rule rockyou --limit 50000000 | hashcat -m {mode} {hashes} --potfile-disable -w 3",
                        "medido": "28,97%"},
            "passgpt": {"desc": "PassGPT neuronal (wordlist passgpt_candidates.txt)",
                        "args": ["-a","0","{hashes}","passgpt_candidates.txt"], "medido": "3,39%"},
        },
    },
}
RECOVERED_RE = re.compile(r"Recovered\.*:\s*(\d+)/(\d+)\s*\(([\d.]+)%\)")

def ollama_chat(messages, force_json=False):
    payload = {"model": MODEL, "messages": messages, "stream": False}
    if force_json: payload["format"] = "json"
    req = urllib.request.Request(OLLAMA_URL, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            return json.loads(r.read())["message"]["content"]
    except urllib.error.URLError as e:
        sys.exit(f"[!] No se pudo hablar con Ollama en {OLLAMA_URL}: {e}\n    docker ps --filter name=ollama")

def ask_plan(hash_type, steps):
    catalogo = "\n".join(f'  - "{k}": {v["desc"]} (recall medido: {v["medido"]})' for k,v in steps.items())
    system = ("Eres el orquestador de un lab de cracking AUTORIZADO (hashes propios). "
              "NO escribes comandos ni inventas metricas. Solo ELIGES pasos de un catalogo fijo y su orden. "
              "Un hash no revela su contrasena: decides por el TIPO de hash.")
    user = (f"Tipo de hash: {hash_type}.\nCatalogo (usa SOLO estos IDs):\n{catalogo}\n\n"
            'Devuelve SOLO un JSON: {"plan":[IDs ordenados de mas barato a mas caro],'
            '"stop_when":"regla de parada","rationale":"por que ese orden"}.')
    raw = ollama_chat([{"role":"system","content":system},{"role":"user","content":user}], force_json=True)
    try: return json.loads(raw)
    except json.JSONDecodeError: sys.exit(f"[!] El LLM no devolvio JSON valido:\n{raw}")

def run_step(step, hashes_file, mode):
    if step.get("pipe"):
        inner = step["pipe"].format(mode=mode, hashes=hashes_file)
        cmd = ["docker","compose","run","--rm","lab","bash","-c",inner]
    else:
        args = [a.replace("{hashes}", hashes_file) for a in step["args"]]
        cmd = ["docker","compose","run","--rm","lab","hashcat","-m",str(mode),*args,"--potfile-disable","-w","3"]
    print("   $ " + " ".join(cmd))
    res = subprocess.run(cmd, capture_output=True, text=True)
    matches = RECOVERED_RE.findall(res.stdout + res.stderr)
    if not matches: return None
    c,t,p = matches[-1]
    return int(c), int(t), float(p)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("hashes"); ap.add_argument("--type", default="ntlm", choices=list(CATALOG.keys()))
    a = ap.parse_args()
    cat = CATALOG[a.type]; steps = cat["steps"]

    print(f"[1] El LLM ({MODEL}) decide la estrategia para '{a.type}'...")
    plan = ask_plan(a.type, steps)
    req = plan.get("plan", [])
    valid = [s for s in req if s in steps]; dropped = [s for s in req if s not in steps]
    if dropped: print(f"   [guard] IDs inventados, descartados: {dropped}")
    print(f"   Plan     : {valid}\n   Parada   : {plan.get('stop_when')}\n   Razon    : {plan.get('rationale')}")

    print("\n[2] Ejecutando la escalera (recall MEDIDO, no estimado):")
    results = []
    for sid in valid:
        step = steps[sid]; print(f"\n -> {sid}: {step['desc']}")
        if not step.get("args") and not step.get("pipe"): print("    (pendiente: se omite)"); continue
        r = run_step(step, a.hashes, cat["mode"])
        if r is None: print("    [error] sin linea 'Recovered'"); continue
        c,t,p = r; print(f"    MEDIDO: {c}/{t} = {p:.2f}%")
        results.append({"paso":sid,"recall_medido_pct":p,"cracked":c})

    print("\n[3] Resumen (todo medido):")
    for r in results: print(f"    {r['paso']:10s} {r['recall_medido_pct']:6.2f}%  ({r['cracked']})")

    if results:
        print("\n[4] El LLM analiza los resultados REALES:")
        print(ollama_chat([
            {"role":"system","content":"Analista de seguridad. 2-3 frases sobre resultados MEDIDOS y siguiente paso. No inventes cifras."},
            {"role":"user","content":f"Tipo: {a.type}. Medido: {json.dumps(results, ensure_ascii=False)}"}]))

if __name__ == "__main__":
    main()
