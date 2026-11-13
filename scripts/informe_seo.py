#!/usr/bin/env python3
"""Informe SEO desde Search Console o exportación CSV. No publica contenido."""
import csv
import datetime as dt
import json
import os
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "seo" / "informes" / "ultimo-informe.md"
PROPERTY = os.environ.get("GSC_PROPERTY", "https://alaezprocurador.github.io/procurador-leon/")
CSV_PATH = os.environ.get("GSC_CSV", "")


def google_rows():
    credentials_json = os.environ.get("GSC_SERVICE_ACCOUNT_JSON", "").strip()
    if not credentials_json:
        return None
    from google.oauth2 import service_account
    from google.auth.transport.requests import Request as AuthRequest
    credentials = service_account.Credentials.from_service_account_info(
        json.loads(credentials_json),
        scopes=["https://www.googleapis.com/auth/webmasters.readonly"],
    )
    credentials.refresh(AuthRequest())
    end = dt.date.today() - dt.timedelta(days=3)
    start = end - dt.timedelta(days=27)
    url = "https://searchconsole.googleapis.com/webmasters/v3/sites/" + quote(PROPERTY, safe="") + "/searchAnalytics/query"
    body = json.dumps({
        "startDate": start.isoformat(), "endDate": end.isoformat(),
        "dimensions": ["query"], "rowLimit": 2500,
        "dataState": "final",
    }).encode()
    request = Request(url, data=body, method="POST", headers={
        "Authorization": "Bearer " + credentials.token,
        "Content-Type": "application/json",
    })
    with urlopen(request, timeout=45) as response:
        data = json.load(response)
    return [{
        "query": row.get("keys", [""])[0],
        "clicks": row.get("clicks", 0),
        "impressions": row.get("impressions", 0),
        "ctr": row.get("ctr", 0),
        "position": row.get("position", 0),
    } for row in data.get("rows", [])]


def parse_number(value):
    s = str(value or "0").strip().replace("%", "").replace(" ", "")
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return 0.0


def csv_rows(path):
    with open(path, encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        rows = []
        for r in reader:
            lower = {str(k).strip().lower(): v for k, v in r.items() if k}
            q = lower.get("query", lower.get("consultas", lower.get("consulta", "")))
            if not q:
                continue
            impressions = parse_number(lower.get("impressions", lower.get("impresiones", 0)))
            clicks = parse_number(lower.get("clicks", lower.get("clics", 0)))
            ctr = parse_number(lower.get("ctr", 0))
            if ctr > 1:
                ctr /= 100
            rows.append({
                "query": q, "impressions": impressions, "clicks": clicks,
                "ctr": ctr, "position": parse_number(lower.get("position", lower.get("posición", 0))),
            })
        return rows


def report(rows, source):
    today = dt.date.today().isoformat()
    output = [
        "# Informe SEO — " + today, "",
        "**Origen:** " + source, "",
        "**Propiedad:** " + PROPERTY, "",
        "Las métricas corresponden al periodo de exportación o, con API, a 28 días cerrados.",
        "No representan estimaciones de demanda ni garantizan posiciones.", "",
    ]
    if not rows:
        output += ["No se recibieron consultas. Verifique los permisos, el periodo y que exista tráfico medible.", ""]
    else:
        impressions = sum(r["impressions"] for r in rows)
        clicks = sum(r["clicks"] for r in rows)
        output += [
            f"Consultas analizadas: **{len(rows)}**. Impresiones sumadas por consulta: **{impressions:,.0f}**. Clics sumados: **{clicks:,.0f}**.",
            "",
            "## Oportunidades de mejora", "",
            "Criterio orientativo: posición media 4–20, al menos 10 impresiones y CTR inferior al 5 %. Revisar intención antes de redactar.",
            "",
            "| Consulta | Impresiones | Clics | CTR | Posición media |",
            "|---|---:|---:|---:|---:|",
        ]
        opportunities = sorted(
            (r for r in rows if 4 <= r["position"] <= 20 and r["impressions"] >= 10 and r["ctr"] < .05),
            key=lambda r: (-r["impressions"], r["position"]),
        )
        for r in opportunities[:20]:
            q = str(r["query"]).replace("|", "\\|").replace("\n", " ")
            output.append(f'| {q} | {r["impressions"]:.0f} | {r["clicks"]:.0f} | {r["ctr"]:.1%} | {r["position"]:.1f} |')
        if not opportunities:
            output.append("| Sin oportunidades que cumplan el filtro | — | — | — | — |")
        output += [
            "", "## Próximas acciones editoriales", "",
            "1. Revisar manualmente la intención de las consultas prioritarias y si ya existe una página que responda.",
            "2. Mejorar primero las páginas existentes; crear una guía nueva solo si aporta contenido diferente y verificable.",
            "3. Enlazar desde la página principal y añadir la URL al sitemap.",
            "4. Revisar los datos del siguiente periodo y registrar contactos reales.", "",
        ]
    output += ["**Control:** este informe no modifica la web ni publica artículos. Las recomendaciones requieren aprobación.", ""]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(output), encoding="utf-8")
    print(f"Informe creado: {OUTPUT}")


def main():
    if CSV_PATH:
        report(csv_rows(CSV_PATH), "CSV exportado de Search Console")
    elif os.environ.get("GSC_SERVICE_ACCOUNT_JSON", "").strip():
        report(google_rows(), "API de Google Search Console")
    else:
        report([], "Sin conexión: configurar GSC_SERVICE_ACCOUNT_JSON o ejecutar con GSC_CSV")
        print("AVISO: no hay credenciales GSC; informe sin datos reales.")


if __name__ == "__main__":
    main()
