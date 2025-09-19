#!/usr/bin/env python3
"""
Script to filter adjectives from kilgariff_adjectives-only file by removing
those that are also present in lemmas_corewn_adj-header file.
"""

def read_adjectives_from_file(filename):
    """
    Read adjectives from a file, skipping the header line.

    Args:
        filename (str): Path to the input file

    Returns:
        set: Set of adjectives (lowercased for case-insensitive comparison)
    """
    adjectives = set()

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()

            # Skip the header line (first line should be "adjective")
            for line in lines[1:]:
                word = line.strip().lower()
                if word:  # Only add non-empty lines
                    adjectives.add(word)

    except FileNotFoundError:
        print(f"Error: Could not find file '{filename}'")
        return set()
    except Exception as e:
        print(f"Error reading file '{filename}': {str(e)}")
        return set()

    return adjectives

def filter_adjectives(kilgariff_file, corewn_file, output_file):
    """
    Filter adjectives from kilgariff file by removing those present in corewn file.

    Args:
        kilgariff_file (str): Path to kilgariff adjectives file
        corewn_file (str): Path to corewn adjectives file
        output_file (str): Path to output filtered file
    """

    print(f"Reading adjectives from {kilgariff_file}...")
    kilgariff_adjectives = []

    # Read kilgariff adjectives preserving order and case
    try:
        with open(kilgariff_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

            # Keep header
            if lines and lines[0].strip().lower() == 'adjective':
                header = lines[0].strip()

                # Store adjectives with original case and order
                for line in lines[1:]:
                    word = line.strip()
                    if word:
                        kilgariff_adjectives.append(word)
            else:
                print("Warning: kilgariff file doesn't start with 'adjective' header")
                return

    except FileNotFoundError:
        print(f"Error: Could not find file '{kilgariff_file}'")
        return
    except Exception as e:
        print(f"Error reading kilgariff file: {str(e)}")
        return

    print(f"Found {len(kilgariff_adjectives)} adjectives in kilgariff file")

    print(f"Reading adjectives from {corewn_file}...")
    corewn_adjectives = read_adjectives_from_file(corewn_file)

    if not corewn_adjectives:
        print("No adjectives found in corewn file or error reading file")
        return

    print(f"Found {len(corewn_adjectives)} unique adjectives in corewn file")

    # Filter kilgariff adjectives
    filtered_adjectives = []
    removed_count = 0

    for adj in kilgariff_adjectives:
        if adj.lower() not in corewn_adjectives:
            filtered_adjectives.append(adj)
        else:
            removed_count += 1

    print(f"Removed {removed_count} adjectives that were present in both files")
    print(f"Remaining adjectives: {len(filtered_adjectives)}")

    # Write filtered results
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            # Write header
            f.write('adjective\n')

            # Write filtered adjectives
            for adj in filtered_adjectives:
                f.write(f'{adj}\n')

        print(f"Filtered adjectives saved to '{output_file}'")

    except Exception as e:
        print(f"Error writing output file: {str(e)}")

def main():
    """Main function to execute the filtering process."""

    kilgariff_file = "data/kilgariff_adjectives-only"
    corewn_file = "data/lemmas_corewn_adj-header"
    output_file = "data/kilgariff_filtered_adjectives.txt"

    print("=" * 60)
    print("Kilgariff Adjectives Filter")
    print("=" * 60)
    print(f"Input file (Kilgariff): {kilgariff_file}")
    print(f"Reference file (CoreWN): {corewn_file}")
    print(f"Output file: {output_file}")
    print("-" * 60)

    filter_adjectives(kilgariff_file, corewn_file, output_file)

    print("=" * 60)
    print("Process completed!")

if __name__ == "__main__":
    main()
