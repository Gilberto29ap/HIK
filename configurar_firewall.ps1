# Script para configurar firewall do Windows para permitir acesso ao servidor Flask no WSL
# Execute este script no PowerShell como Administrador

$port = 5000
$ruleName = "WSL Flask Server"

# Remove regra existente se houver
Write-Host "Removendo regra antiga (se existir)..."
Remove-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue

# Cria nova regra de firewall
Write-Host "Criando regra de firewall para porta $port..."
New-NetFirewallRule -DisplayName $ruleName -Direction Inbound -LocalPort $port -Protocol TCP -Action Allow

Write-Host "✓ Firewall configurado com sucesso!"
Write-Host "O servidor agora deve estar acessível na rede interna."
