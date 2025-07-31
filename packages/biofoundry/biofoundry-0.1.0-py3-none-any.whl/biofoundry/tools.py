def convert_md_txt(md_txt, data=None):
    delimiter = "```"

    if data is None:
        data = {}
    identifier = None
    current_entry = {}
    lines = md_txt.split("\n")
    # Split header and main:
    delimiter_counter = 0
    for index, line in enumerate(lines):
        if line.strip() == "```":
            delimiter_counter += 1
            if delimiter_counter == 2:
                split_index = index
                break
    header_lines = lines[1:split_index]  # exclude delimiter lines
    main_lines = lines[split_index + 1 :]  # exclude closing delimiter

    for line in main_lines:

        if line.startswith("- "):
            # New entry, save previous entry
            if identifier and current_entry:
                data[identifier] = current_entry
                current_entry = {}
            # Extract the identifier label
            identifier, name = line.split(":", maxsplit=1)
            identifier = identifier.strip("- *")
            name = name.strip()

            current_entry["name"] = name

        elif line.startswith("  - **"):
            label, text = line.split(":", maxsplit=1)
            label = label.strip("- *")
            text = text.strip()

            current_entry[label] = text

        elif line.startswith("  -"):  # workflow entry description
            current_entry["Description"] = line.strip(" -")

    # last entry
    if current_entry:
        data[identifier] = current_entry

    return header_lines, data
