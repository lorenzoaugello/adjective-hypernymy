import csv
import wn
import argparse

# Uncomment to download the OEWN
#wn.download("oewn:2024)

fix_definitions = {
    "especially of psychological coldness; without human warmth or emotion ": "oewn-01260684-a",
    "of the color between blue and yellow in the color spectrum": "oewn-00380557-s",
    "not containing meat": "oewn-82572455-a",
    "capable of preventing conception or impregnation": "oewn-01893918-s",
    "indicating the most important performer or role": "oewn-00888020-a"
    }

def comp_defns(def1, def2):
    return def1 == def2 or def1 in def2 or def2 in def1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert OEWN to RDF")
    parser.add_argument("input", help="Input CSV file")
    parser.add_argument("output", help="Output RDF file")
    args = parser.parse_args()

    # Load OEWN
    wordnet = wn.Wordnet("oewn:2024")

    # Read the CSV file
    with open(args.input, "r", encoding="utf-8") as csvfile:
        with open(args.output, "w", encoding="utf-8") as rdffile:
            rdffile.write(
                    """@prefix oewn: <http://en-word.net/id/> .
@prefix wn: <http://globalwordnet.github.io/schemas/wn.rdf#>

""")
            reader = csv.DictReader(csvfile, delimiter=";")
            for row in reader:
                hypo_lemmas = [lemma.strip() for lemma in row["hyponym-lemma"].split(",")]
                hypos = [s for hypo_lemma in hypo_lemmas for s in wordnet.synsets(hypo_lemma)]
                hypos = [h for h in hypos if comp_defns(row["hypo_definition"], h.definition())]
                if len(hypos) < 1:
                    hypo_id = fix_definitions[row["hypo_definition"]]
                else:
                    hypo_id = hypos[0].id

                hyper_lemmas = [lemma.strip() for lemma in row["hypernym-lemma"].split(",")]
                hypers = [s for hyper_lemma in hyper_lemmas for s in wordnet.synsets(hyper_lemma)]
                hypers = [h for h in hypers if comp_defns(row["hyper_definition"], h.definition())]

                if len(hypers) < 1:
                    hyper_id = fix_definitions[row["hyper_definition"]]
                else:
                    hyper_id = hypers[0].id

                if not hyper_id:
                    print(hypers)

                rdffile.write("oewn:{} wn:hypernym oewn:{} .\n".format(
                    hypo_id, hyper_id))






