import discord


class DiceEmbed:
    @staticmethod
    def build_dice_embed(dice_groups, dice_results, modifiers, total):
        """Build embed for dice roll results"""
        embed = discord.Embed(title="🎲 Les dés roulent et ...", color=0x0000FF)

        # Add dice groups results
        for (count, faces), rolls in zip(dice_groups, dice_results):
            group_total = sum(rolls)
            rolls_str = ", ".join(str(r) for r in rolls)
            embed.add_field(
                name=f"{count}d{faces} = {group_total}", value=rolls_str, inline=True
            )

        # Add modifiers if any
        if modifiers:
            mod_str = " + ".join(str(m) for m in modifiers)
            embed.add_field(name="Modificateur(s)", value=mod_str, inline=True)

        # Add total
        embed.add_field(name="Total", value=str(total), inline=True)

        return embed
