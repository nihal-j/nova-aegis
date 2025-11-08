from pathlib import Path
p = Path("OPENROUTER_API_KEY.txt")
if p.exists():
    print("OPENROUTER_API_KEY.txt already exists; not overwriting.")
else:
    key = input("Paste your OPENROUTER API key (starts with 'sk-') and press Enter: ").strip()
    p.write_text(key)
    print("Saved to OPENROUTER_API_KEY.txt and (should be) gitignored.")
