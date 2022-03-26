
import Shared

pses = Shared.Psutil.find(name='dotnet')
for ps in pses:
    ps.kill()

print(f"Found {len(pses)}")