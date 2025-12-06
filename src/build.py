# build.py - Script para compilar o Pomodoro Timer em .exe

import PyInstaller.__main__
import sys
import os
from pathlib import Path

def build_exe():
    """Compila o app em um executável standalone"""
    
    print("🐱 Compilando Pomodoro Timer...")
    print("=" * 50)
    
    # Caminho base do projeto
    base_path = Path(__file__).parent
    
    # Separator correto para Windows/Linux
    separator = ';' if os.name == 'nt' else ':'
    
    # Argumentos do PyInstaller
    args = [
        'pomodoro.py',                          # Arquivo principal
        '--name=PomoCat',                 # Nome do executável
        '--onefile',                            # Arquivo único
        '--windowed',                           # Sem console
        '--icon=web/assets/icon.ico',          # Ícone (se tiver)
        f'--add-data=web{separator}web',       # Inclui pasta web
        '--clean',                              # Limpa cache
        '--noconfirm',                          # Não pede confirmação
        
        # Remove imports desnecessários para reduzir tamanho
        '--exclude-module=matplotlib',
        '--exclude-module=pandas',
        '--exclude-module=numpy',
        '--exclude-module=scipy',
        '--exclude-module=PIL',
        
        # Metadados (Windows)
        '--version-file=version.txt',           # Se tiver arquivo de versão
    ]
    
    # Remove o --icon se não existir
    icon_path = base_path / 'web' / 'assets' / 'icon.ico'
    if not icon_path.exists():
        args = [arg for arg in args if not arg.startswith('--icon')]
        print("⚠️  Aviso: icon.ico não encontrado, compilando sem ícone")
    
    # Remove version file se não existir
    version_path = base_path / 'version.txt'
    if not version_path.exists():
        args = [arg for arg in args if not arg.startswith('--version-file')]
    
    try:
        # Executa PyInstaller
        PyInstaller.__main__.run(args)
        
        print("\n" + "=" * 50)
        print("✅ Compilação concluída com sucesso!")
        print(f"📦 Executável criado em: dist/PomodoroTimer.exe")
        print("=" * 50)
        
        # Instruções
        print("\n📋 Próximos passos:")
        print("1. Teste o executável: dist/PomodoroTimer.exe")
        print("2. Distribua o arquivo .exe para quem quiser!")
        print("3. Não precisa instalar Python para rodar 🎉")
        
    except Exception as e:
        print(f"\n❌ Erro durante compilação: {e}")
        sys.exit(1)


if __name__ == '__main__':
    build_exe()