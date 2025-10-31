import json
import re
from models import DomainRequest


def build_prompt(req: DomainRequest) -> str:
    styles_text = ", ".join(req.styles) if req.styles else "any style"
    misspell_text = "Yes" if req.include_misspelling else "No"
    max_w = req.max_words if req.max_words and req.max_words > 0 else 2

    # Force natural proportional mix based on max_words
    if max_w == 1:
        combo_description = "Generate only single-word brand names."
    elif max_w == 2:
        combo_description = (
            "Generate a mix of single-word and two-word merged brand names "
            "(for example: 'TechNest', 'Flowva', 'QuickCart')."
        )
    else:
        combo_description = (
            f"Generate a balanced variety of 1-word, 2-word, and 3-word merged brand names. "
            f"Roughly 30% 1-word, 40% 2-word, and 30% 3-word combinations. "
            "Each name should look like one single word — no spaces or hyphens."
        )

    return f"""
You are a highly creative domain naming assistant.

Task:
Generate up to 200 short, catchy, and brandable domain name ideas (WITHOUT extensions like .com or .io).

Business Description:
{req.description}

Guidelines:
- Domain Style(s): {styles_text}
- Include legible misaspellings or abbreviations: {misspell_text}
- {combo_description}
- Each domain name should sound natural, relevant to the business, and be easy to pronounce.
- Avoid real company names or trademarks.
- Use capitalization only for readability in multi-word merges (e.g., "BlueOceanHub").
- Do not include punctuation, hyphens, or spaces.
- Keep each name under 15 characters if possible.

Output Format:
Return ONLY a valid JSON array of strings. No extra text, no explanations, no code fences.

Example output:
["Shopify", "QuickCart", "BlueOceanHub", "NextWaveAI", "Flowva", "SmartBuildPro"]
"""




def parse_model_output(raw_text: str):
    """Clean up markdown/code-fenced output and return a list of domain names."""
    cleaned = re.sub(r"```(?:json|JSON)?", "", raw_text).strip()

    # Try parsing JSON first
    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed, list):
            return [s.strip() for s in parsed if isinstance(s, str)]
    except json.JSONDecodeError:
        pass

    # Fallback: extract line-separated items
    lines = [line.strip("-• \n\t") for line in cleaned.split("\n") if line.strip()]
    return lines[:20]







import socket
from typing import List


def check_domain_availability(domains: List[str], extension: str) -> List[str]:
    """Combine domain names with extension and return available ones."""
    available_domains = []

    # Normalize extension
    ext = extension.strip()
    if not ext.startswith("."):
        ext = f".{ext}"

    for name in domains:
        domain = f"{name.strip().lower()}{ext}"

        try:
            # Try to resolve the domain
            socket.gethostbyname(domain)
            # If resolved, domain is registered
        except socket.gaierror:
            # Unresolvable → likely available
            available_domains.append(domain)
        except Exception:
            # Any unexpected error → skip safely
            continue

    return available_domains

import os
import httpx
from typing import List

async def check_domain_availability_ninjas(domains: List[str]) -> List[str]:
    """
    Check real-time domain availability using API Ninjas Domain API.
    Returns a list of domains that are NOT registered.
    """
    API_KEY = os.getenv("NINJAS_API_KEY")
    API_URL = "https://api.api-ninjas.com/v1/domain"
    if not API_KEY:
        raise RuntimeError("❌ NINJAS_API_KEY missing in .env file")

    available = []
    headers = {
        "X-Api-Key": API_KEY,
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        for name in domains:
            domain = f"{name.strip().lower()}"
            try:
                # Correct query parameter
                resp = await client.get(f"{API_URL}?domain={domain}", headers=headers)
                print(f"Checked {domain}: {resp.status_code}, {resp.text}")

                if resp.status_code == 200:
                    data = resp.json()
                    # The API returns "is_registered": True/False
                    print(f"Response data for {domain}: {data} ${data.get("available", False)}")
                    if data.get("available", False):
                        available.append(domain)
                else:
                    print(f"⚠️ Skipped {domain}: {resp.status_code}")

            except Exception as e:
                print(f"⚠️ Error checking {domain}: {e}")
                continue

    return available
