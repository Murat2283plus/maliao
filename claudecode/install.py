#!/usr/bin/env python3
"""
Installation script for Matrix Mario
"""
import os
import sys
import subprocess
import platform

def check_python_version():
    """Check if Python version is sufficient"""
    if sys.version_info < (3, 7):
        print("Error: Python 3.7 or higher is required")
        return False
    print(f"✓ Python {sys.version} detected")
    return True

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✓ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing requirements: {e}")
        return False

def setup_permissions():
    """Setup file permissions on Unix systems"""
    if platform.system() != 'Windows':
        # Make run scripts executable
        scripts = ['run_console.py', 'run_gui.py']
        for script in scripts:
            if os.path.exists(script):
                os.chmod(script, 0o755)
                print(f"✓ Made {script} executable")

def check_hardware():
    """Check for connected hardware"""
    print("\\nChecking hardware...")
    
    # Check for game controllers
    try:
        import pygame
        pygame.init()
        pygame.joystick.init()
        
        controller_count = pygame.joystick.get_count()
        if controller_count > 0:
            for i in range(controller_count):
                joystick = pygame.joystick.Joystick(i)
                joystick.init()
                print(f"✓ Controller detected: {joystick.get_name()}")
        else:
            print("⚠ No game controllers detected")
            print("  Please connect a PS5 controller for full functionality")
        
        pygame.quit()
    except ImportError:
        print("⚠ Could not check for controllers (pygame not installed)")
    
    # Check for serial ports
    try:
        import serial.tools.list_ports
        ports = list(serial.tools.list_ports.comports())
        if ports:
            print("\\nAvailable serial ports:")
            for port in ports:
                print(f"  - {port.device}: {port.description}")
        else:
            print("⚠ No serial ports detected")
            print("  Use --mock-serial flag for testing without hardware")
    except ImportError:
        print("⚠ Could not check serial ports (pyserial not installed)")

def create_shortcuts():
    """Create desktop shortcuts (Windows only)"""
    if platform.system() == 'Windows':
        try:
            import winshell
            desktop = winshell.desktop()
            
            # Create shortcut for console version
            console_shortcut = os.path.join(desktop, "Matrix Mario Console.lnk")
            with winshell.shortcut(console_shortcut) as link:
                link.path = sys.executable
                link.arguments = os.path.abspath("run_console.py")
                link.working_directory = os.path.abspath(".")
                link.description = "Matrix Mario Console Version"
            
            # Create shortcut for GUI version
            gui_shortcut = os.path.join(desktop, "Matrix Mario GUI.lnk")
            with winshell.shortcut(gui_shortcut) as link:
                link.path = sys.executable
                link.arguments = os.path.abspath("run_gui.py")
                link.working_directory = os.path.abspath(".")
                link.description = "Matrix Mario GUI Version"
            
            print("✓ Desktop shortcuts created")
        except ImportError:
            print("⚠ Could not create desktop shortcuts (winshell not available)")

def main():
    """Main installation function"""
    print("Matrix Mario Installation Script")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install requirements
    if not install_requirements():
        return False
    
    # Setup permissions
    setup_permissions()
    
    # Check hardware
    check_hardware()
    
    # Create shortcuts (Windows only)
    if platform.system() == 'Windows':
        create_shortcuts()
    
    print("\\n" + "=" * 40)
    print("Installation complete!")
    print("\\nTo run Matrix Mario:")
    print("  Console mode: python run_console.py")
    print("  GUI mode:     python run_gui.py")
    print("\\nFor testing without hardware:")
    print("  python run_console.py --mock-serial")
    print("\\nSee README.md for detailed usage instructions.")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)