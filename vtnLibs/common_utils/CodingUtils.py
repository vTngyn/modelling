import re
from icecream import ic

class StringUtils():
    char_map_list = [
        {'a':['ä', 'â', 'à']}
        ,{'e':['ö', 'ô']}
        ,{'u':['û', 'ü', 'ù']}
        ,{'e': ['ö', 'ô', 'é', 'è']}
        ,{'i':['î', 'ï', 'ì']}
        ,{'c':['ç']}
    ]

    char_mappings = [
        ('ä', 'a'), ('â', 'a'), ('à', 'a'),
        ('ö', 'o'), ('ô', 'o'),
        ('û', 'u'), ('ü', 'u'), ('ù', 'u'),
        ('ö', 'e'), ('ô', 'e'), ('é', 'e'), ('è', 'e'),
        ('î', 'i'), ('ï', 'i'), ('ì', 'i'),
        ('ç', 'c')
    ]

    @staticmethod
    def substitute_characters(input_string, ):
        # Create a dictionary from the list of mappings for easy lookup
        char_map = {char_to_use: chars_to_substitute for char_to_use, chars_to_substitute in StringUtils.char_map_list}

        # Initialize an empty result string
        result_string = ""

        # Iterate through each character in the input string
        for char in input_string:
            # Check if the character is in any of the substitution lists
            for char_to_use, chars_to_substitute in char_map.items():
                if char in chars_to_substitute:
                    # Replace the character with the char_to_use
                    char = char_to_use
                    break  # Stop searching for this character

            # Append the character (either substituted or unchanged) to the result string
            result_string += char

        return result_string



    def substitute_characters_regex(input_string, char_mappings=None):
        if not char_mappings:
            char_mappings=StringUtils.char_mappings
        # Create a regex pattern for matching characters to be substituted
        pattern = "|".join([re.escape(char_to_find) for char_to_find, _ in char_mappings])

        # Create a substitution function to map characters to their replacements
        def substitute(match):
            char_to_find = match.group(0)
            #ic(char_to_find)
            for char_to_use, char_replacing in char_mappings:
                if char_to_find == char_to_use:
                    return char_replacing
            return char_to_find

        # Use re.sub() with the substitution function to perform the replacement
        result = re.sub(pattern, substitute, input_string)

        return result


if __name__ == "__main__":
    input_string = "This is a sample sentence with some characters to be replaced: äâà öô üûù éè îïì ç."


    result = StringUtils.substitute_characters_regex(input_string)
    input_string_val = "This is a sample sentence with some characters to be replaced: aaa oo uuu ee iii c."

    ic(result)
    ic(f"match?:{True if result == input_string_val else False}")
