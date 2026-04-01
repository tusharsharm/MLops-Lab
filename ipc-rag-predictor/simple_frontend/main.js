const statusEl = document.getElementById('status');
const respEl = document.getElementById('response');
const form = document.getElementById('predict-form');

async function checkHealth(){
  try{
    const r = await fetch('/health');
    if(r.ok) statusEl.textContent = 'ok';
    else statusEl.textContent = 'unhealthy';
  }catch(e){
    statusEl.textContent = 'offline';
  }
}

form.addEventListener('submit', async (ev)=>{
  ev.preventDefault();
  const q = document.getElementById('q').value;
  respEl.textContent = 'waiting...';
  try{
    const r = await fetch('/predict', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({question: q})
    });
    const data = await r.json();
    respEl.textContent = JSON.stringify(data, null, 2);
  }catch(e){
    respEl.textContent = String(e);
  }
});

checkHealth();
