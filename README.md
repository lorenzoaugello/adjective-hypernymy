## adjective-hypernymy
This repository was created to store the dataset that was constructed for representing the lexical relation of hypernymy (is-a relation) for English adjectives. 
The lemmas were extracted from two existing lexical resources, the Polish WordNet and the Open Dutch WordNet, and then manually translated into English.
The gold standard dataset with hyponym-hypernym pairs and their definitions taken from the Open English WordNet is stored in the file 'gold.csv'.
This is then divided into a training set and a test set, which have been used for the evaluation of language models performances on tasks of hypernymy discovery and lexical entailment: 
'hypernymy-testset-single.csv' and 'hypernymy-train-single.csv' contain only one hypernym for each hyponym, while 'hypernymy-testset-multiple.csv' and 'hypernymy-train-multiple.csv' contain more than one hypernym for each hyponym, as their synonyms extracted from the Open English WordNet were also included to solve issues of word sense disambiguation and polysemy.
