import sys
sys.path.insert(0, '.')

with open('test_result.txt', 'w', encoding='utf-8') as f:
    try:
        from app.routes import formula_routes
        f.write("formula_routes imported OK\n")
        f.write(f"Routes: {[r.path for r in formula_routes.router.routes]}\n")
    except Exception as e:
        f.write(f"Error: {e}\n")

    try:
        from app.services.gemini_service import GeminiService
        gs = GeminiService()
        f.write("GeminiService OK\n")
        f.write(f"Has explain_formula: {hasattr(gs, 'explain_formula')}\n")
    except Exception as e:
        f.write(f"GeminiService Error: {e}\n")

print("Done - check test_result.txt")
