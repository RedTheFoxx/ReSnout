import subprocess
import platform
import discord

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

def generate_system_info_commands() -> str:
    """
    Generate a string containing shell commands to gather system information.
    
    Returns:
        str: A string of shell commands.
    """
    commands = [
        "lscpu",
        "free -h",
        "df -h"
    ]
    return "; ".join(commands)

def run_system_info_commands() -> dict:
    """
    Execute the system information commands and gather the output.
    
    Returns:
        dict: A dictionary containing the output of each command.
    """
    commands = generate_system_info_commands()
    try:
        # Run the commands and capture the output
        result = subprocess.run(commands, shell=True, check=True, text=True, capture_output=True)
        
        # Split the output into parts corresponding to each command
        outputs = result.stdout.strip().split('\n\n')
        
        # Define keys for each command output
        keys = ["CPU Information", "Memory Usage", "Disk Usage"]
        
        # Create a dictionary with keys and corresponding outputs
        info_dict = {keys[i]: outputs[i] for i in range(len(keys))}
        
        return info_dict
    
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while executing the commands: {e}")
        return {"Error": str(e)}

def create_system_embeds(system_info: dict) -> list[discord.Embed]:
    """
    Create Discord embeds for system information.
    
    Args:
        system_info (dict): Dictionary containing system information
        
    Returns:
        list[discord.Embed]: List of embeds for CPU, Memory and Disk information
    """
    cpu_embed = discord.Embed(title="CPU Information", color=discord.Color.blue())
    cpu_embed.description = f"```\n{system_info['CPU Information']}\n```"
    
    memory_embed = discord.Embed(title="Memory Usage", color=discord.Color.green())
    memory_embed.description = f"```\n{system_info['Memory Usage']}\n```"
    
    disk_embed = discord.Embed(title="Disk Usage", color=discord.Color.gold())
    disk_embed.description = f"```\n{system_info['Disk Usage']}\n```"
    
    return [cpu_embed, memory_embed, disk_embed] 