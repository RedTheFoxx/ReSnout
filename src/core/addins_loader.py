"""Plugin loading operations for ReSnout. 'Addins' is the internal name for plugins."""

from plugins.SimpleOps.SO import SimpleOps


class AddinLoader:
    def __init__(self, bot):
        self.bot = bot
        self.loaded_plugins = []

    async def load_plugin(self, plugin_class, plugin_name):
        """Load a single plugin and add it to the loaded plugins list."""
        try:
            await self.bot.add_cog(plugin_class(self.bot))
            self.loaded_plugins.append(plugin_name)
            print(f"✅ Successfully loaded plugin: {plugin_name}")
            return True
        except Exception as e:
            print(f"❌ Failed to load plugin {plugin_name}: {str(e)}")
            return False

    async def load_all_plugins(self):
        """Load all available plugins."""
        print("\n📦 Starting plugin loading sequence...")
        
        # Load SimpleOps (mandatory plugin)
        await self.load_plugin(SimpleOps, "SimpleOps")
        
        # Here we can add more plugins as they become available
        
        print(f"\n✨ Plugin loading complete! Loaded {len(self.loaded_plugins)} plugins:")
        for plugin in self.loaded_plugins:
            print(f"   • {plugin}")
        print("")
