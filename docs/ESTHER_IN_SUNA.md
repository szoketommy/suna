# Demo da Esther no sandbox do agentiK (Daytona)

Passo a passo para rodar o agente Esther diretamente no sandbox do agentiK (via chat).

## 1) No chat do agentiK
Peça para o agente executar comandos em sandbox e cole o bloco abaixo:

```bash
cat > task.json <<'EOF'
{"project":"Esther Orbiter","goal":"Demo run via agentiK sandbox","params":{"mode":"status_report","lang":"pt-PT"}}
EOF
git clone https://github.com/19721102/esther-orbiter.git
cd esther-orbiter
bash scripts/agentik_agent_bootstrap.sh ../task.json
cat out_agentik/result.json
ls -la out_agentik
```

> Antes de rebuildar o frontend local, copie `frontend/.env.example` para `frontend/.env.local` e rode `docker-compose up -d --build`.

## 2) Artefatos esperados
- `out_agentik/result.json`
- `out_agentik/report.txt`
- `out_agentik/run.log`

Esses arquivos são gerados pelo bootstrap e contêm o resultado, relatório e log do run.
