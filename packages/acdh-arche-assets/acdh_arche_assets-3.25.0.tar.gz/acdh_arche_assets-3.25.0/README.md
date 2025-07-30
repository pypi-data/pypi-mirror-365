# Arche Assets

[![PyPI version](https://badge.fury.io/py/acdh-arche-assets.svg)](https://badge.fury.io/py/acdh-arche-assets)
[![codecov](https://codecov.io/gh/acdh-oeaw/arche-assets/branch/master/graph/badge.svg?token=RFOH77TBV1)](https://codecov.io/gh/acdh-oeaw/arche-assets)
[![Test](https://github.com/acdh-oeaw/arche-assets/actions/workflows/pytest.yml/badge.svg)](https://github.com/acdh-oeaw/arche-assets/actions/workflows/pytest.yml)
[![flake8 Lint](https://github.com/acdh-oeaw/arche-assets/actions/workflows/pylint.yml/badge.svg)](https://github.com/acdh-oeaw/arche-assets/actions/workflows/pylint.yml)
[![Latest Stable Version](https://poser.pugx.org/acdh-oeaw/arche-assets/v/stable)](https://packagist.org/packages/acdh-oeaw/arche-assets)
[![phpunit](https://github.com/acdh-oeaw/arche-assets/actions/workflows/php.yml/badge.svg)](https://github.com/acdh-oeaw/arche-assets/actions/workflows/php.yml)
[![License](https://poser.pugx.org/acdh-oeaw/arche-assets/license)](https://packagist.org/packages/acdh-oeaw/arche-assets)

Set of static assets used (mainly) for ARCHE data preprocessing or ARCHE information pages:
* URI normalization rules used within the [ACDH-CH](https://www.oeaw.ac.at/acdh/).\
  (stored in `AcdhArcheAssets/uriNormRules.json`)
* Description of input data formats accepted by [ARCHE](https://arche.acdh.oeaw.ac.at).\
  (stored in `AcdhArcheAssets/formats.json`)

The repository provides also Python 3 and PHP bindings for accessing those assets.

# Installation & usage

## Python

* Install using pip3:
  ```bash
  pip3 install acdh-arche-assets
  ```
* Use with
  ```Python
  from AcdhArcheAssets.uri_norm_rules import get_rules, get_normalized_uri, get_norm_id
  print(f"{get_rules()}")

  wrong_id = "http://sws.geonames.org/1232324343/linz.html"

  good_id = get_normalized_uri(wrong_id)
  print(good_id)
  # "https://sws.geonames.org/1232324343/"

  # extract ID from URL
  norm_id = get_norm_id("http://sws.geonames.org/1232324343/linz.html")
  print(norm_id)
  # "1232324343"


  from AcdhArcheAssets.file_formats import get_formats, get_by_mtype, get_by_extension

  formats = get_formats()
  matching_mapping = get_by_mtype('image/png')
  matching_mapping = get_by_extension('png')
  
  ```

## PHP

* Install using using [composer](https://getcomposer.org/doc/00-intro.md):
  ```bash
  composer require acdh-oeaw/arche-assets
  ```
* Usage with
  ```php
  require_once 'vendor/autoload.php';

  print_r(acdhOeaw\UriNormRules::getRules());
  print_r(acdhOeaw\UriNormRules::getRules(['viaf', 'gnd']));

  print_r(acdhOeaw\ArcheFileFormats::getAll();
  print_r(acdhOeaw\ArcheFileFormats::getByMime('application/json');
  print_r(acdhOeaw\ArcheFileFormats::getByExtension('application/json');
  ```

# Description of assets

## URI normalization rules

Each rule consists of five properties:

* `name`: a rule name
* `match`: a regular expression matching a given URI namespace
* `replace`: a regular expression replace expression normalizing an URI in a given namespace
* `resolve`: a regular expression replace expression transforming an URI in a given namespace to an URL fetching an RDF data
* `format`: a RDF serialization format to be requested while resolving the URL produced using the `resolve` field

## Formats

A curated and growing list of file extensions. For each file extension mappings to the respective [ARCHE Resource Type Category]( 	https://vocabs.acdh.oeaw.ac.at/archecategory/Schema) (stored in `acdh:hasCategory`) and [Media Type (MIME type)](https://www.iana.org/assignments/media-types/media-types.xhtml) (stored in `acdh:hasFormat`) are given. The indicated Media Type should only be used as a fallback; it is best practice to rely on automated Media Type detection based on file signatures.

Further information is provided as well.

* fileExtension: File extension to be mapped.
* name: Name(s) the format is known
* archeCategory: The corresponding URI of the [ARCHE Resource Type Category Vocabulary](https://vocabs.acdh.oeaw.ac.at/archecategory/Schema)
* dataType: A broad category to group formats in; mainly intended for visualisation purposes.
* pronomID: ID(s) assigned by [PRONOM](http://www.nationalarchives.gov.uk/PRONOM/Default.aspx)
* mimeType: Official Media Type(s) (formerly known as MIME types) registered at [IANA](https://www.iana.org/assignments/media-types/media-types.xhtml).
* informalMimeType: Other MIME types kown for the format
* magicNumber: A constant numerical or text value used to identify a file format, e.g. [Wikipedia list of file signatures](https://en.wikipedia.org/wiki/List_of_file_signatures)
* ianaTemplate: Link to template at IANA
* reference: Link(s) to format specifications referenced by IANA and others
* longTerm: Indicates if a format is suitable for long-term preservation.\
  Possible values and their meaning
   * yes - long-term format
   * no - not suitable, another format should be used
   * restricted - can be used for long-term preservation in some cases (see comment)
   * unsure - status remains to be evaluated
* archeDocs: Link to a place with more information for the format.
* comment: Any other noteworthy information not stated elsewhere.

# Developement (Python)

install needed developement packages `pip install requirements_dev.txt`

## linting, tests and testcoverage

* to run the test: `tox`
* check coverage and create report: `coverage run setup.py test` and `coverage html`
* check linting `flake8`
