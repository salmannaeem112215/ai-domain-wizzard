from fastapi import FastAPI, HTTPException
from openai import OpenAI
from dotenv import load_dotenv
import os

from models import DomainCheckRequest, DomainCheckResponse, DomainRequest, DomainResponse
from services import build_prompt, parse_model_output,check_domain_availability,check_domain_availability_ninjas

# ===============================
# App and Environment Setup
# ===============================
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
ninjas_key = os.getenv("NINJAS_API_KEY")

print(f"✅ Loaded OpenAI Key: {bool(api_key)}")
print(f"✅ Loaded Ninjas Key: {bool(ninjas_key)}")

if not api_key:
    raise RuntimeError("❌ OPENAI_API_KEY not found in .env file")

app = FastAPI(title="Domain Name Generator API", version="1.1")
client = OpenAI(api_key=api_key)


from fastapi import FastAPI, HTTPException
from openai import OpenAI
from dotenv import load_dotenv
import os

from models import DomainRequest, DomainResponse
from services import (
    build_prompt,
    parse_model_output,
    check_domain_availability_ninjas,
)

# ===============================
# App and Environment Setup
# ===============================
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise RuntimeError("❌ OPENAI_API_KEY not found in .env file")

app = FastAPI(title="Domain Wizard API", version="1.0")
client = OpenAI(api_key=api_key)
def normalize_domains(domains, extension):
    """
    Remove any extensions from generated domains to avoid duplicates.
    """
    normalized = []
    for d in domains:
        if d.endswith(f".{extension}"):
            d = d[:-(len(extension)+1)]  # remove ".com" etc
        normalized.append(d)
    return normalized

# ===============================
# Unified API Endpoint
# ===============================
@app.post("/domain-wizard", response_model=DomainResponse)
async def domain_wizard(req: DomainRequest):
    """
    Generate ~domain ideas, filter locally, then check actual availability via API Ninjas.
    """
    try:
        # ------------------------------
        # Step 1: Generate domain ideas using OpenAI
        # ------------------------------
        prompt = build_prompt(req)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a creative and precise domain name generator."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.8,
            max_tokens=10000,  # increase tokens to get more domains (~)
        )

        text_output = response.choices[0].message.content.strip()
        suggestions = parse_model_output(text_output)

        print(f"Generated {len(suggestions)} suggestions from model. ${suggestions}")

        # ------------------------------
        # Step 2: Clean, deduplicate, normalize
        # ------------------------------
        clean_suggestions = list(dict.fromkeys([s.strip().lower() for s in suggestions if s.strip()]))
        print(f"Cleaned to {len(clean_suggestions)} unique suggestions. ${clean_suggestions}")
        # Normalize: remove any extensions already included
        normalized_suggestions = [
            s[:-len(req.extension)-1] if s.endswith(f".{req.extension}") else s
            for s in clean_suggestions
        ]
        print(f"Normalized suggestions: {normalized_suggestions}")
        if not normalized_suggestions:
            raise HTTPException(status_code=400, detail="No valid domain suggestions generated.")

        # ------------------------------
        # Step 3: Filter using local availability check
        # ------------------------------
        filtered_domains = check_domain_availability(normalized_suggestions, req.extension)
        # Limit to ~40 to pass to API Ninjas
        print(f"Filtered to {len(filtered_domains)} domains after local check. ${filtered_domains}")
        if not filtered_domains:
            raise HTTPException(status_code=404, detail="No domains passed local availability check.")

        # ------------------------------
        # Step 4: Check availability using API Ninjas
        # ------------------------------
        available_domains = await check_domain_availability_ninjas(filtered_domains)
        print(f"\n\nAvaliable to {len(available_domains)} domains after local check. ${available_domains}")

        # ------------------------------
        # Step 6: Return results
        # ------------------------------
        return DomainResponse(
            available_domains=available_domains,
            suggestions=clean_suggestions,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# ===============================
# API Endpoint
# ===============================
@app.post("/generate-domains", response_model=DomainResponse)
async def generate_domains(req: DomainRequest):
    try:
        prompt = build_prompt(req)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful and precise domain name generator."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.8,
            max_tokens=400,
        )

        text_output = response.choices[0].message.content.strip()
        suggestions = parse_model_output(text_output)

        # Ensure clean, unique, limited results
        clean_suggestions = list(dict.fromkeys([s for s in suggestions if s]))[:20]

        return DomainResponse(suggestions=clean_suggestions)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")










@app.post("/check-domains", response_model=DomainCheckResponse)
async def check_domains(req: DomainCheckRequest):
    try:
        available = check_domain_availability(req.names, req.extension)
        return DomainCheckResponse(available_domains=available)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")





# @app.post("/check-domains-thirdparty", response_model=DomainCheckResponse)
# async def check_domains_ninjas(req: DomainCheckRequest):
#     try:
#         available = await check_domain_availability_ninjas(req.names)
#         return DomainCheckResponse(available_domains=available)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error: {str(e)}")