#!/usr/bin/env python3
import tempfile
from pathlib import Path
from quality_gate import check

def main():
 with tempfile.TemporaryDirectory() as d:
  p=Path(d)/"article.html"
  p.write_text("<h1>Test update</h1><p>"+("Useful factual content for a factual article. "*30)+"</p><h2>Sources</h2><p>https://example.com/source</p>",encoding="utf-8")
  p.with_suffix(".json").write_text('{"sources":[{"url":"https://example.com/source"}]}',encoding="utf-8")
  ok,errors=check(p); assert ok,errors
 print("quality_gate_test=PASS")
if __name__=="__main__": main()
