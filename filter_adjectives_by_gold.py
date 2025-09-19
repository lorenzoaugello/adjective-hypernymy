#!/usr/bin/env python3
"""
Script to filter adjectives from adjectives_def.csv by removing those that are
present in the hyponym-lemma column of gold.csv file.
"""

import csv
import sys

gold_file = './data/initial-gold/gold.csv'

def read_gold_hyponyms(./data/initial-gold/gold.csv):
    """
    Read hyponym adjectives from gold.csv file.

    Args:
        gold_file (str): Path to the gold.csv file

    Returns:
        set: Set of hyponym adjectives (lowercased for case-insensitive comparison)
    """
    gold_hyponyms = set()

    try:
        with open(gold_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')

            for row in reader:
                hyponym = row.get('hyponym-lemma', '').strip().lower()
                if hyponym:
                    gold_hyponyms.add(hyponym)

    except FileNotFoundError:
        print(f"Error: Could not find file '{gold_file}'")
        return set()
    except Exception as e:
        print(f"Error reading gold file '{gold_file}': {str(e)}")
        return set()

    return gold_hyponyms

def filter_adjectives_by_gold(adjectives_file, gold_file, output_file):
    """
    Filter adjectives from adjectives_def.csv by removing those present in gold.csv.

    Args:
        adjectives_file (str): Path to adjectives_def.csv file
        gold_file (str): Path to gold.csv file
        output_file (str): Path to output filtered file
    """

    print(f"Reading gold hyponyms from {gold_file}...")
    gold_hyponyms = read_gold_hyponyms(gold_file)

    if not gold_hyponyms:
        print("No hyponyms found in gold file or error reading file")
        return

    print(f"Found {len(gold_hyponyms)} unique hyponyms in gold file")

    print(f"Reading and filtering adjectives from {adjectives_file}...")

    filtered_rows = []
    removed_count = 0
    total_count = 0

    try:
        with open(adjectives_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                total_count += 1
                hyponym = row.get('hyponym', '').strip()

                if hyponym.lower() not in gold_hyponyms:
                    filtered_rows.append(row)
                else:
                    removed_count += 1

    except FileNotFoundError:
        print(f"Error: Could not find file '{adjectives_file}'")
        return
    except Exception as e:
        print(f"Error reading adjectives file: {str(e)}")
        return

    print(f"Total adjectives processed: {total_count}")
    print(f"Removed {removed_count} adjectives that were present in gold file")
    print(f"Remaining adjectives: {len(filtered_rows)}")

    # Write filtered results
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            if filtered_rows:
                fieldnames = filtered_rows[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)

                writer.writeheader()
                for row in filtered_rows:
                    writer.writerow(row)

        print(f"Filtered adjectives saved to '{output_file}'")

    except Exception as e:
        print(f"Error writing output file: {str(e)}")

def main():
    """Main function to execute the filtering process."""

    adjectives_file = "data/adjectives_def.csv"
    gold_file = "data/initial-gold/gold.csv"
    output_file = "data/adjectives_def_filtered.csv"

    print("=" * 60)
    print("Adjectives Filter by Gold Dataset")
    print("=" * 60)
    print(f"Adjectives file: {adjectives_file}")
    print(f"Gold file: {gold_file}")
    print(f"Output file: {output_file}")
    print("-" * 60)

    filter_adjectives_by_gold(adjectives_file, gold_file, output_file)

    print("=" * 60)
    print("Filtering completed!")

if __name__ == "__main__":
    main()
