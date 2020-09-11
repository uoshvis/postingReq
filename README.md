# postingReq

## Introduction

Simple interface for getting CVbankas postings with brutto salary converter
to netto using Sodra converter api.

## Installation

The `requirements.txt` file should list all Python libraries that your notebooks
depend on, and they will be installed using:

```
pip install -r requirements.txt
```
## Parameters

* `city`

  - optional
  - city of interest

* `keyword`

  - optional
  - key of interest

## Example

```
from postingReq import PostingReq

obj = PostingReq(city='Vilnius', keyword='Autocad')
result = obj.postings_by_salary()
```