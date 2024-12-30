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
        self.registered_commands = {}
        self.config_path = Path(__file__).parent.parent / "plugins" / "pluginslist.toml"

    def _load_config(self):
        """Load the plugins configuration from TOML file."""
        try:
            return toml.load(self.config_path.open())
        except Exception as e:
            print(f"❌ Failed to load plugin configuration: {e}")
            return None

    def _get_plugin_commands(self, plugin_class):
        """Extract all commands from a plugin class."""
        return [
            m.name
            for m in inspect.getmembers(plugin_class)
            if isinstance(m, app_commands.Command)
        ]

    def _check_command_conflicts(self, plugin_name, commands):
        """Check if any command from the plugin conflicts with existing ones."""
        return [
            (cmd, self.registered_commands[cmd])
            for cmd in commands
            if cmd in self.registered_commands
        ]

    async def _load_plugin(self, plugin_name, plugin_config):
        """Load a single plugin using its configuration."""
        try:
            module = importlib.import_module(plugin_config["path"])
            plugin_class = getattr(module, plugin_config["class"])
            commands = self._get_plugin_commands(plugin_class)

            if conflicts := self._check_command_conflicts(plugin_name, commands):
                conflict_msg = "\n".join(
                    f"Command /{cmd} already registered by plugin {existing_plugin}"
                    for cmd, existing_plugin in conflicts
                )
                print(f"❌ Plugin {plugin_name} has command conflicts:\n{conflict_msg}")
                if plugin_config.get("required", False):
                    raise Exception(
                        f"Required plugin {plugin_name} has command conflicts"
                    )
                return False

            self.registered_commands.update({cmd: plugin_name for cmd in commands})
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
        if not (config := self._load_config()):
            raise Exception("Failed to load configuration.")

        required_plugins_failed = []
        for plugin_name in config["plugins"]["enabled"]:
            if plugin_name not in config:
                print(f"❌ Configuration missing for plugin: {plugin_name}")
                continue

            success = await self._load_plugin(plugin_name, config[plugin_name])
            if not success and config[plugin_name].get("required", False):
                required_plugins_failed.append(plugin_name)

        if required_plugins_failed:
            for plugin_name in required_plugins_failed:
                print(f"Required plugin {plugin_name} failed to load. Closing ...")
            raise Exception(
                f"Required plugins failed to load: {', '.join(required_plugins_failed)}"
            )

        print(
            f"\n✨ Plugin loading complete! Loaded {len(self.loaded_plugins)} total plugins."
        )

    async def load_plugins(self):
        """Load plugins (only if called from main.py)"""
        caller_path = inspect.getfile(inspect.currentframe().f_back).replace("\\", "/")
        main_path = str(Path(__file__).parent.parent / "main.py").replace("\\", "/")

        if caller_path == main_path:
            await self._load_all_plugins()
        else:
            print("❌ Plugin loading can only be initiated from main.py")
            raise Exception("Plugin loading can only be initiated from main.py")

    async def get_loaded_plugins(self):
        return self.loaded_plugins
