#!/usr/bin/env python3
import json,re,sys
from pathlib import Path
from urllib.parse import urlparse
MIN_WORDS=80
BLOCKED=(r"guaranteed returns",r"guaranteed profit",r"buy now",r"risk[- ]free investment",r"click here to earn")
def check(path):
 p=Path(path); errors=[]
 if not p.is_file(): return False,["article file does not exist"]
 html=p.read_text(encoding="utf-8")
 plain=re.sub(r"\s+"," ",re.sub(r"<[^>]+>"," ",html)).strip()
 count=len(re.findall(r"\b[\w₹$%.-]+\b",plain))
 if "<h1" not in html.lower(): errors.append("missing h1")
 if count<MIN_WORDS: errors.append(f"too short: {count} words; minimum {MIN_WORDS}")
 if "sources" not in plain.lower(): errors.append("missing Sources section")
 urls=re.findall(r'https?://[^\s"<>]+',html)
 if not any(urlparse(u).scheme in ("http","https") for u in urls): errors.append("no source URLs found")
 for pat in BLOCKED:
  if re.search(pat,plain.lower()): errors.append("blocked editorial phrase: "+pat)
 meta=p.with_suffix(".json")
 if not meta.is_file(): errors.append("source metadata file missing")
 else:
  try:
   if not json.loads(meta.read_text(encoding="utf-8")).get("sources"): errors.append("metadata contains no sources")
  except Exception as e: errors.append("invalid metadata: "+str(e))
 return not errors,errors
if __name__=="__main__":
 if len(sys.argv)!=2: raise SystemExit("Usage: quality_gate.py ARTICLE.html")
 ok,errors=check(sys.argv[1]); print("QUALITY_GATE=PASS" if ok else "QUALITY_GATE=FAIL")
 for e in errors: print(" -",e)
 raise SystemExit(0 if ok else 1)
