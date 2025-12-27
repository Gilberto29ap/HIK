# Como acessar o servidor Flask do WSL na rede

## Problema
O WSL2 usa uma rede NAT virtualizada, e o Windows Firewall bloqueia conexões externas por padrão.

## Solução

### Opção 1: Configurar Firewall (Recomendado)

1. **Abra o PowerShell como Administrador** (no Windows, não no WSL)
2. Execute o script:
   ```powershell
   cd \\wsl$\Ubuntu\home\kvra\HIK
   .\configurar_firewall.ps1
   ```

### Opção 2: Configurar manualmente via GUI

1. Abra o **Firewall do Windows** → Configurações avançadas
2. Clique em **Regras de Entrada**
3. Clique em **Nova Regra**
4. Selecione **Porta** → Avançar
5. Selecione **TCP** e digite **5000** → Avançar
6. Selecione **Permitir a conexão** → Avançar
7. Marque todas as opções (Domínio, Privado, Público) → Avançar
8. Dê um nome: "WSL Flask Server" → Concluir

### Opção 3: Encontrar o IP do Windows e acessar por ele

No WSL, execute:
```bash
ip route show | grep -i default | awk '{ print $3}'
```

Use este IP com a porta 5000 para acessar de outros dispositivos na rede.

## Testando o acesso

1. **No Windows**, abra o navegador e acesse:
   ```
   http://localhost:5000
   ```

2. **De outro dispositivo na rede**, primeiro descubra o IP do Windows:
   - No PowerShell (Windows): `ipconfig`
   - Procure por "Adaptador Ethernet" ou "Adaptador Wireless" → IPv4
   - Acesse: `http://[IP_DO_WINDOWS]:5000`

## Verificar se o servidor está rodando

No WSL:
```bash
curl http://localhost:5000
```

## Portas abertas no WSL

Para ver se o servidor está escutando:
```bash
netstat -tulpn | grep 5000
```
