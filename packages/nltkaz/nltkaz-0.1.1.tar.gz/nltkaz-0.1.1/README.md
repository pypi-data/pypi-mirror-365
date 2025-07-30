![NLTKaz Banner](https://i.imgur.com/NRajui2.png)

# NLTKAZ 📚

**NLTKAZ** is a natural language processing toolkit designed for the Azerbaijani language making it easier to preprocess Azerbaijani text for NLP tasks.

## Installation ⬇️
```bash
pip install nltkaz
```

## Features 🧩
Currently following features are provided with the version 0.1.1:
- **Stemming**: Reduce words to their root forms.
- **Stopword Removal**: Easily remove common Azerbaijani stopwords from text.

## Usage ⚙️
### Stemming
```python
from azstemmer import AzStemmer

# Initialize stemmer with the appropriate keyboard type
# Use 'az' for Azerbaijani text or 'en' if the text is typed using an English keyboard
stemmer = AzStemmer(keyboard="az") 

# Stem your string
stemmed_string = stemmer.stem("your_string")
```

### Stopword Removal
```python
from nltkaz.stopwords import load, remove

# load stopwords using
stopwords = load()
# remove stopwords from the given string
result = remove(stopwords=stopwords, sentence="your_string")
```

## Author 🧑‍💻
- **Nagi Nagiyev**  

## Contact 📧
Gmail: nagiyevnagi01@gmail.com.

Linkedin: https://www.linkedin.com/in/naginagiyev/

## License 📜
MIT License

---

> This project is in early development. Contributions and feedback are welcome! 🤝