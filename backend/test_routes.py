import sys
sys.path.insert(0, '.')

from app.routes.chat_routes import router

with open('routes_output.txt', 'w') as f:
    f.write("Chat routes:\n")
    for route in router.routes:
        f.write(f"  {route.methods} {route.path}\n")
    f.write("\nDone!")

print("Output written to routes_output.txt")
