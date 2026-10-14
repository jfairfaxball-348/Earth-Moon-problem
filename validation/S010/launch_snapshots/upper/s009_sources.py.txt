"""Actual external primary repository API observations; read-only provenance."""
import datetime,json,subprocess
from pathlib import Path
rows=[]
for ep in ('repos/Volkopat/earth-moon-biplanar/commits/main','repos/Volkopat/earth-moon-chi10'):
    r=subprocess.run(['gh','api',ep],capture_output=True,text=True,encoding='utf-8')
    row=dict(endpoint=ep,returncode=r.returncode,stderr=r.stderr)
    try:row['response']=json.loads(r.stdout)
    except ValueError:row['stdout']=r.stdout
    rows.append(row)
Path('validation/S009/source_refresh.json').write_text(json.dumps(dict(
    as_of_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),observations=rows,
    external_proofs_executed=False),indent=1)+'\n',encoding='utf-8',newline='\n')
print('Recorded actual primary repository API responses')
