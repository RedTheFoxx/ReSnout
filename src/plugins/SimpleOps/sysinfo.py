import subprocess
import platform
import discord
import os

def is_raspberry_pi() -> bool:
    """
    Check if the current system is a Raspberry Pi.
    
    Returns:
        bool: True if running on a Raspberry Pi, False otherwise.
    """
    try:
        with open('/proc/cpuinfo', 'r') as f:
            return 'Raspberry Pi' in f.read()
    except:
        return False

def get_memory_info() -> str:
    """Read memory information from /proc/meminfo"""
    try:
        with open('/proc/meminfo', 'r') as f:
            mem_info = []
            for line in f:
                if any(field in line for field in ['MemTotal', 'MemFree', 'MemAvailable', 'SwapTotal', 'SwapFree']):
                    # Convert KB to GB
                    parts = line.split()
                    if len(parts) >= 2:
                        name = parts[0].rstrip(':')
                        value = int(parts[1])
                        gb_value = value / 1024 / 1024  # Convert KB to GB
                        mem_info.append(f"{name}: {gb_value:.2f} GB")
        return '\n'.join(mem_info)
    except Exception as e:
        return f"Error reading memory info: {str(e)}"

def get_disk_info() -> str:
    """Read disk information from /proc/mounts and statvfs"""
    try:
        disk_info = []
        with open('/proc/mounts', 'r') as f:
            for line in f:
                parts = line.split()
                if len(parts) >= 2 and parts[1] == '/':  # Only show root filesystem
                    device = parts[0]
                    mountpoint = parts[1]
                    try:
                        stats = os.statvfs(mountpoint)
                        total = (stats.f_blocks * stats.f_frsize) / (1024**3)  # Convert to GB
                        free = (stats.f_bfree * stats.f_frsize) / (1024**3)
                        used = total - free
                        disk_info.extend([
                            f"Device: {device}",
                            f"Mount: {mountpoint}",
                            f"Total: {total:.2f} GB",
                            f"Used: {used:.2f} GB",
                            f"Free: {free:.2f} GB",
                            f"Use%: {(used/total*100):.1f}%"
                        ])
                    except Exception as e:
                        disk_info.append(f"Error getting stats for {mountpoint}: {str(e)}")
        return '\n'.join(disk_info)
    except Exception as e:
        return f"Error reading disk info: {str(e)}"

def get_system_info() -> dict:
    """
    Gather system information by reading system files.
    
    Returns:
        dict: A dictionary containing system information.
    """
    return {
        "Memory Usage": get_memory_info(),
        "Disk Usage": get_disk_info()
    }

def create_system_embeds(system_info: dict) -> list[discord.Embed]:
    """
    Create Discord embeds for system information.
    
    Args:
        system_info (dict): Dictionary containing system information
        
    Returns:
        list[discord.Embed]: List of embeds for Memory and Disk information
    """
    memory_embed = discord.Embed(title="Memory Usage", color=discord.Color.green())
    memory_embed.description = f"```\n{system_info['Memory Usage']}\n```"
    
    disk_embed = discord.Embed(title="Disk Usage", color=discord.Color.gold())
    disk_embed.description = f"```\n{system_info['Disk Usage']}\n```"
    
    return [memory_embed, disk_embed] 