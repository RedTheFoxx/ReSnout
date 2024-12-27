"""
Plugin loading operations for ReSnout. 'Addins' is the internal name for plugins.
Only the main entrypoint is authorized to load the plugins. Exposes some getters.
"""

import toml
import importlib
from pathlib import Path
import inspect
from discord.ext import commands
from discord import app_commands


class AddinLoader:
    def __init__(self, bot):
        self.bot = bot
        self.loaded_plugins = []
        self.registered_commands = {}  # {command_name: plugin_name}
        self.config_path = Path(__file__).parent.parent / "plugins" / "pluginslist.toml"

    def _load_config(self):
        """Load the plugins configuration from TOML file."""
        try:
            with open(self.config_path, "r") as f:
                return toml.load(f)

        except Exception as e:
            print(f"❌ Failed to load plugin configuration: {e}")
            return None

    def _get_plugin_commands(self, plugin_class):
        """Extract all commands from a plugin class."""
        commands = []
        for _, member in inspect.getmembers(plugin_class):
            if isinstance(member, app_commands.Command):
                commands.append(member.name)
        return commands

    def _check_command_conflicts(self, plugin_name, commands):
        """Check if any command from the plugin conflicts with existing ones."""
        conflicts = []
        for cmd in commands:
            if cmd in self.registered_commands:
                conflicts.append((cmd, self.registered_commands[cmd]))
        return conflicts

    async def _load_plugin(self, plugin_name, plugin_config):
        """Load a single plugin using its configuration."""
        try:
            # Import the module dynamically
            module = importlib.import_module(plugin_config["path"])

            # Get the plugin class
            plugin_class = getattr(module, plugin_config["class"])

            # Check for command conflicts before loading
            commands = self._get_plugin_commands(plugin_class)
            conflicts = self._check_command_conflicts(plugin_name, commands)
            
            if conflicts:
                conflict_msg = "\n".join([f"Command /{cmd} already registered by plugin {existing_plugin}" 
                                        for cmd, existing_plugin in conflicts])
                print(f"❌ Plugin {plugin_name} has command conflicts:\n{conflict_msg}")
                
                if plugin_config.get("required", False):
                    raise Exception(f"Required plugin {plugin_name} has command conflicts")
                return False

            # Register commands and load the plugin
            for cmd in commands:
                self.registered_commands[cmd] = plugin_name

            # Initialize and add the plugin
            await self.bot.add_cog(plugin_class(self.bot))
            self.loaded_plugins.append(plugin_name)

            print(f"✅ Successfully loaded plugin: {plugin_name}")
            return True

        except Exception as e:
            print(f"❌ Failed to load plugin {plugin_name}: {str(e)}")

            if plugin_config.get("required", False):
                raise Exception(f"Required plugin {plugin_name} failed to load")
            return False

    async def _load_all_plugins(self):
        """Load all enabled plugins from configuration."""
        print("\n📦 Starting plugin loading sequence...")

        config = self._load_config()
        if not config:
            raise Exception("Failed to load configuration.")

        enabled_plugins = config["plugins"]["enabled"]
        required_plugins_failed = []

        for plugin_name in enabled_plugins:
            if plugin_name in config:
                success = await self._load_plugin(plugin_name, config[plugin_name])
                if not success and config[plugin_name].get("required", False):
                    required_plugins_failed.append(plugin_name)
            else:
                print(f"❌ Configuration missing for plugin: {plugin_name}")

        if required_plugins_failed:
            for plugin_name in required_plugins_failed:
                print(f"Required plugin {plugin_name} failed to load. Closing ...")
            raise Exception(
                f"Required plugins failed to load: {', '.join(required_plugins_failed)}"
            )

        print(
            f"\n✨ Plugin loading complete! Loaded {len(self.loaded_plugins)} plugins:"
        )
        for plugin in self.loaded_plugins:
            print(f"   • {plugin}")
        print("")

    async def load_plugins(self):
        """Load plugins (only if called from main.py)"""
        caller_frame = inspect.currentframe().f_back
        caller_file_path = inspect.getfile(caller_frame)
        main_file_path = str(Path(__file__).parent.parent / "main.py").replace("\\","/")

        if caller_file_path.replace("\\","/") == main_file_path:
            await self._load_all_plugins()
        else:
            print("❌ Plugin loading can only be initiated from main.py")
            raise Exception("Plugin loading can only be initiated from main.py")

    async def get_loaded_plugins(self):
        return self.loaded_plugins
