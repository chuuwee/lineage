class_dict = {
    "Bard": ["Minstrel", "Troubadour", "Virtuoso"],
    "Beastlord": ["Primalist", "Animist", "Savage Lord"],
    "Berserker": ["Brawler", "Vehement", "Rager"],
    "Cleric": ["Vicar", "Templar", "High Priest"],
    "Druid": ["Wanderer", "Preserver", "Hierophant"],
    "Enchanter": ["Illusionist", "Beguiler", "Phantasmist"],
    "Magician": ["Elementalist", "Conjurer", "Arch Mage"],
    "Monk": ["Disciple", "Master", "Grandmaster"],
    "Necromancer": ["Heretic", "Defiler", "Warlock"],
    "Paladin": ["Cavalier", "Knight", "Crusader"],
    "Ranger": ["Pathfinder", "Outrider", "Warder"],
    "Rogue": ["Rake", "Blackguard", "Assassin"],
    "Shadow Knight": ["Reaver", "Revenant", "Grave Lord"],
    "Shaman": ["Mystic", "Luminary", "Oracle"],
    "Warrior": ["Champion", "Myrmidon", "Warlord"],
    "Wizard": ["Channeler", "Evoker", "Sorcerer"]
}

class_name_by_alias = {}
for true_class, aliases in class_dict.items():
  for alias in aliases:
    class_name_by_alias[alias] = true_class
  class_name_by_alias[true_class] = true_class
