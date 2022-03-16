A toolkit for early Middle English lemmatization based on data from
![eLALME](http://www.lel.ed.ac.uk/ihd/laeme2/laeme2.html) (eMEl).

What `manx` does is that
	* it creates a dictionary of IDs and lemmas key-value pairs
	* it generates a list of n-grams from the corpus
	* it lets you train word embeddings with
	  ![FastText](https://fasttext.cc/docs/en/support.html)


## Why `FastText`?

Here are the reasons:
	1. It incorporates sub-word information by splitting all words into a bag
	   of n-gram characters
	2. Thanks to sub-words, it supports out-of-vocabulary words; it might help
	   with wicked Middle English word forms.
	3. It uses skip-gram objective with randomized negative sampling.

