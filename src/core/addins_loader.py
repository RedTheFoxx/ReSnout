"""Plugin loading operations for ReSnout. 'Addins' is the internal name for plugins."""

import toml
import importlib
from pathlib import Path


class AddinLoader:
    def __init__(self, bot):
        self.bot = bot
        self.loaded_plugins = []
        self.config_path = Path(__file__).parent.parent / "plugins" / "pluginslist.toml"

    def load_config(self):
        """Load the plugins configuration from TOML file."""
        try:
            with open(self.config_path, "r") as f:
                return toml.load(f)

        except Exception as e:
            print(f"❌ Failed to load plugin configuration: {e}")
            return None

    async def load_plugin(self, plugin_name, plugin_config):
        """Load a single plugin using its configuration."""
        try:
            # Import the module dynamically
            module = importlib.import_module(plugin_config["path"])

            # Get the plugin class
            plugin_class = getattr(module, plugin_config["class"])

            # Initialize and add the plugin. A cog is a class that contains commands and events.
            await self.bot.add_cog(plugin_class(self.bot))

            self.loaded_plugins.append(plugin_name)

            print(f"✅ Successfully loaded plugin: {plugin_name}")
            return True

        except Exception as e:
            print(f"❌ Failed to load plugin {plugin_name}: {str(e)}")

            if plugin_config.get("required", False):
                raise Exception(f"Required plugin {plugin_name} failed to load")
            return False

    async def load_all_plugins(self):
        """Load all enabled plugins from configuration."""
        print("\n📦 Starting plugin loading sequence...")

        config = self.load_config()
        if not config:
            raise Exception("Failed to load configuration.")

        enabled_plugins = config["plugins"]["enabled"]
        required_plugins_failed = []

        for plugin_name in enabled_plugins:
            if plugin_name in config:
                success = await self.load_plugin(plugin_name, config[plugin_name])
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
