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

def generate_system_info_commands() -> list:
    """
    Generate a list of shell commands to gather system information.
    
    Returns:
        list: A list of shell commands.
    """
    return ["lscpu", "free -h", "df -h"]

def run_system_info_commands() -> dict:
    """
    Execute the system information commands and gather the output.
    
    Returns:
        dict: A dictionary containing the output of each command.
    """
    commands = generate_system_info_commands()
    info_dict = {}
    
    try:
        # Run each command separately
        for i, cmd in enumerate(commands):
            result = subprocess.run(cmd.split(), capture_output=True, text=True, check=True)
            if i == 0:
                info_dict["CPU Information"] = result.stdout
            elif i == 1:
                info_dict["Memory Usage"] = result.stdout
            elif i == 2:
                info_dict["Disk Usage"] = result.stdout
        
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