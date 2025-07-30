# Time to text


Command to run unit tests from project directory:
# python -m unittest discover -s tests

## Installation

```
pip install convert_time_to_text
```

## Usage
```
from convert_time_to_text import convert_time_to_text

print(convert_time_to_text(5,00))
print(convert_time_to_text(5,0))
print(convert_time_to_text(5,1))
print(convert_time_to_text(5,9))
print(convert_time_to_text(5,10))
print(convert_time_to_text(5,15))
print(convert_time_to_text(5,30))
print(convert_time_to_text(5,37))
print(convert_time_to_text(5,40))
print(convert_time_to_text(5,45))
print(convert_time_to_text(5,47))
print(convert_time_to_text(12,24))
print(convert_time_to_text(11,50))
print(convert_time_to_text(12,50))
print(convert_time_to_text(12,20))
```
### Given the time in numerals we may convert it into words, as shown below:
The above should result in the following output:
```
five o' clock
five o' clock
one minute past five
nine minutes past five
ten minutes past five
quarter past five
half past five
twenty three minutes to six
twenty minutes to six
quarter to six
thirteen minutes to six
twenty four minutes past twelve
ten minutes to twelve
ten minutes to one
twenty minutes past twelve
```
