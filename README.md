# <center>Redactor</center>
Created a command line script that can redact names, dates places, concepts, addresses and phone numbers (Created Mar-Apr 2018).

## Redactor and Unredactor
FILE Organization:

	redactor/
		redactor/
			__init__.py
			redactor.py
			unredactor.py

		tests/
			test_rm_names.py
			test_rm_phones.py
			test_rm_genders.py
			test_rm_addresses.py
			test_rm_concept.py
			test_rm_dates.py
			tets_find_entity.py
		DATA/
			retxt/
			testfiles/
				pos/
				neg/
			trainfiles/
				pos/
				neg/
		README
		requirements.txt
		setup.cfg
		setup.py

NOTE : 
-REMOVED DATA file to reduce upload size for Github.

-Instead of docs/ I have added DATA folder which consists of 4000 aclImdb text files. These were used to test the undredactor.py.
 retxt consists of the test files after redaction.

- Redactor and unredactor have been set to take only the first 50 files in a given directory to keep the testing time short. To take all the files change the following:

For unredactor: comment LINE 24 and uncomment LINE 25.

For redactor: comment LINE 24 and uncomment LINE 23.

#### redactor.py
The redactor will take in the text files given in a specific directory and output in the specified output directory. Any of the following flags can be used to redact the required content.

An example of the command line input. The following was used to redact the names from the testfiles to create content for the unredactor.py. 

This needs to begiven in the following format when in the directory '/projects/redactor/redactor':

	python3 redactor.py --input "/projects/redactor/data/testfiles/pos/*.txt" --input "/projects/redactor/data/testfile/neg/*.txt" --output "/projects/redactor/data/retxt/" --names

Here removing names and then printing the priting the statistics.
	python3 redactor.py --input "/projects/redactor/data/trainfiles/pos/*.txt" 
		    --output "/projects/redactor/data/retxt/" 
		    --names 
		    --stats stdout

#### INPUT:
The input was done using glob.glob hence we must give the input directory in quotes. otherwise the linux will perform the same action and an error will occur.

#### OUTPUT:
The output directory also needs to specified in the above manner. We used regex to detect and compare the last two files. If they match then the file name will be "original_filename.redacted.txt" otherwise it will be written to the 
output file with the original filename.

### <center>Flags</center>
All flagged/redacted phrases or string chunks are replaced with '█' (U+2588) and any redaction refers to this.
##### 1) Names: --names:
Input- Document or String
Output- Redacted document or string, list of redacted names for testing
Functioning:
-The method rm_names() performs whenever the command line argument contains "--names".We are using the ne_chunk from nltk here to identify the names. The doc is passed to nltk's word_tokenizer as a whole. Then passed to pos_tagger 
and then to ne_chunk. 
-ne_chunk returns "chunks" which are tuples containtg the pos tag and the name entity if the phrase is one. If the phrase is a named entity then it is returned as a Tree. If a name containing mulitple words is present then it
 retuend inside a single Tree object of which we use only the "PERSON" tags. The words in the "PERSON" trees are then added to a list  which is then soreted such that all the names in s descending order by length. 
this is important as if a name is repeated but only a part of the name is used, then if the smaller name (say "John") will replace the text in "John Williams"; resulting in "John Williams" --> "████ Williams". So to prevent this we are 
replacing the longer strings first. After this the redacted document along with the list of redacted names is returned.

Bugs:
- Sometimes the ne_chunk is identifying the words with capital letters in the beginning as names.  Ex "Sit" is classfied as a person in "Sit back, relax".
- Names containing hyphens(-) are not being identified as shown in test case example.
- STANFORD NER was tried but was not successful due to issues with importing .jar files required.

##### 2) Genders: --genders:
Input- Document or String
Output- Redacted document or string, list of redacted gender referances for testing.
Functioning:
-rm_genders() has been created to identify any words that identify the gender and redact them.The first approach was to try synset lemmas for words like "her, him, woman" etc. This did not do well. Then a corpus was created including
 the correct results from the synet lemms and obvious gender referential words.
-Any obvious words revealing the gender of a person are also removed. This was done by creating a regex patterns for words starting and ending with boy,girl,man,men. 
-Another set of regex patterns was created to remove female centric words like actress, countess which ended with "ess". But this could occur in other words such as "Butress,press" etc. hence regex was created to omit these words. the
 document was word tokenized and then checked with the Corpus and then the regexes. 
-All tokens are converted to lowercases. Each word ans sentence is recreated. Moses Detokenizer is used for this. To maintain the integirty of the document regarding '\n' we split and join with '\n' all the sentences.
-"https://www.thefreedictionary.com/words-that-end-in-my" was used to explore other words that might clash our regex patterns. 

Bugs:
-Unexpected behaviour due to the regex patterns coinciding with other words.
-Not completely capturing professional or other words which reveal the gender.

##### 3) Dates: --dates:
Input- Document or String
Output- Redacted document or string, list of redacted strings considered dates for testing.
Functioning:
- rm_dates() was created for this. The dateutil.parser package was used for this.
- The doc is first split based on '\n',then word tokenized. The we send it to a try block containing the date parser. If the string does not contain any dates or times then an exception is thrown.This is caught in the except block. 
This way we skip any words that are not dates. If the string does have a date then the parser does not throw an error and this part of the string is redacted. The replacement string containing █ is appended to the list which is used 
for recosntruction of the doc.

Bugs:
-The dateutil.parser classfies any number also as a date. This has been included in he test case. We tried datefinder but the same is repeated in some cases for datefinder package too. The parser expects all the string inputs to 
be dates. This approach needs to change.

##### 4) Adresses: --addresses:
Input- Document or String
Output- Redacted document or string, list of redacted strings considered an address for testing.
Functioning:
-rm_addresses was used to remove the strings considered an address. The package usaddress was used. It takes in a sentence and tags each of the phrase as different parts of an address.
-After splitting by '\n' we input the whole sentence and it spits out tuples with tags for each word. it assumes that the entire string is an address hence tags the entire thing. The tags were filtered out empirically. The tags 
'BuildingName', 'Recipient', 'OccupancyType', 'OccupancyIdentifier' and 'LandmarkName' were the tags that were used for the strings that were most likely not addresses. The pther tags were allowed to be replaced by the redactor.

Bugs:
-It is not able to identify cities and pin codes in some cases. The usaddress parser by default assumes that all the input is address to be parsed.
-The address needs to be in a standard format like "14, Board Dr., Norman, OK".

##### 5) Phones: --phones:
Input- Document or String
Output- Redacted document or string, list of redacted phone numbers.
Functioning:
-rm_phones is used to get rid of the phone numbers. Primarily regex was used to get identify the phone numbers. re.findall() is used which returns the list of matched strings.
-These are again sorted just to make sure that a shorter version of the same phone number does not cause problems like with names.Ex : "000 0000" would replace "000 000 0000" but only partially if the shorter version comes first in
 the list.

-The following regex pattern was used to identify the string:
		((\+\d{11,13})|(\+\d{1,3}[\s\-\.])?(\(?\d{3}\)?[\s\.\-]?)?\d{3}[\s\.\-]?\d{4})

Bugs:
-Any conflicting string patterns not actually phone numbers will also be identified as phone numbers.

##### 6) Concepts: --concept <concept to be redacted>:
Input- Document or String, Concept ot be redacted
Output- Redacted document or string, Number of lines redacted
Functioning:
- We use the WORDNET lexical database for this task. Wordnet consists of synsets. Each synset for a word is linked to other synsets through conceptual-semantic and lexical relations.
-We retrieve the synset for the concept and then pull the related synsets using hypernyms, hyponyms and holonyms. After this we extract the all the lemmas from these synsets and then compare them with the words in document.
-The document is divided using sent tokenizer and then word tokenizer. Then we check if the word is present in the lemmas extracted. If it is then we raise a FLAG(set FLAG = TRUE). If the flag is True for a sentence, then we redact 
the entire sentence. We use the same method as befoe to recosntruct the document. Use Moses Detokenizer and the join by '\n'.

Bugs:
- synsets work better when they know whether the given word is verb or noun. Due to the lack of this the accuracy of the other sysnsets retreived is bad and sometimes they are compeltely unrelated. Ex: sysnet('eat') finally a lemma 
"garbage". Another example is that "prison" sysnet does not contain the lemmas "incarcerated" or "jail" in the linked synsets.

##### 7)--stats <argument>:
-Prints out the name of the file and the number of a type of entity redacted in that file to output_statistics in data/ folder.
-It takes exactly one command line argument which can be either 'stdout' or 'out'. When stdout is given then the statistics are also printed on the screen. Each type of the above flags are printed one after the another.
- output_stats.txt is created at the location of the redactor.py. This text file consists of the statistics for each of the file for each flag.

Bugs:
-MUST GIVE either stdout or any other string otherwise will throw an error.

##### Unredactor.py
The unredactor takes the training files and the redacted test files and gives an output file containing the predictions for the redacted names in the test file.
The undredactor command expects atleast on input to train the model with.

Command Line Arguments:
a)--train
Pass the files directories containing the ".txt" files that will be used to train. for this project we have stored 2000 training files in DATA/trainfiles/. The command line input looks similar to  theinput for the redactor.
The given files are sent to find_entity(). The find _entity uses the ne_chunk to find the names and then extracts the features around the name.

find_entity: It takes in the document and the document name and gives out a list of  dictionary containing the features realted to the names found in the file. The features collected here are:
	-Target: NAME of the person
	-Length of the first word in the name
	-Length of the second word in the name
	-length of the third word in the name
	-length of total name
	-Number of words
	-Rating of the movie
Other features were collected but only managed to reduce the training accuracy. They were the chunk befre the name,document length, pos_tag of the chunk befpore the name. These seem to worsen the model accuracy on the train dataset.

b)--test
-We need to pass files with redacted names here. The files are sent to the get_entity_test(). This takes redacted files and collects the same features as above but with no name and returns a list of dictionaries. The get_entity_test 
extracts the features around █ blocks. The --train location that is given must have atleast one redacted in isde the file. Otherwise an error will thrown as predict() needs atleast one datapoint to make a prediction on.

-The lists of dicts are collected to two lists. DictVectroizer's fit_tranform is used on the train dicts features list and the numpy array for the deatures is obtained. The same dictvectorizer is used on the test dict list. 
-An MLPclassifier is trained through the fit() method and then the predict() method is used to predict the values for the test set. Accuracy on the train set varies with change in number of files being given. As the number of files 
increases the classes also increase. This increases the difficulty of the problem. The predicted values are then printed out to redactor/data/pred_names.txt.
Various other classifers such as Guassian NaiveBayes, KNeibhours classifier etc. MLP seems to b performing the best.

-This needs to begiven in the following format when in the directory '/projects/redactor/redactor':

			python3 unredactor.py --train "/projects/redactor/data/trainfiles/pos/*.txt" --test "/projects/redactor/data/retxt/*.txt"

We use the glob.glob<directory>) to get all the the possible text files inside that directory and extract the strings inside to "train" and "test" arrays. 
-pred_names.txt is created in the location of the unredactor.py file. This contains all the predicted names.
-Unless Cross Validation is performed we can not determine which model is the best as one model might perform better by chance.

Bugs:
-We MUST give test and train files containing atleast one entity of name and redacted name respectively. Otherwise errors will arise while training and predicting.

