#!/usr/bin/env python
# coding=utf-8
# Copyright 2017 The Tensor2Tensor Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""A simple invertible tokenizer.

Converts from a unicode string to a list of tokens
(represented as Unicode strings).

This tokenizer has the following desirable properties:
 - It is invertible.
 - Alphanumeric characters are broken away from non-alphanumeric characters.
 - A single space between words does not produce an extra token.
 - The full Unicode punctuation and separator set is recognized.

The tokenization algorithm is as follows:

1.  Split the text into a list of tokens, splitting at every boundary of an
    alphanumeric character and a non-alphanumeric character.  This produces
    a list which alternates between "alphanumeric tokens"
    (strings of alphanumeric characters) and "non-alphanumeric tokens"
    (strings of non-alphanumeric characters).

2.  Remove every token consisting of a single space, unless it is
    the very first or very last token in the list.  These tokens are now
    implied by the fact that there are two adjacent alphanumeric tokens.

e.g.  u"Dude - that's so cool."
        -> [u"Dude", u" - ", u"that", u"'", u"s", u"so", u"cool", u"."]
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections
import sys
import unicodedata

# Dependency imports

import six
from six.moves import xrange  # pylint: disable=redefined-builtin
#import tensorflow as tf

# Conversion between Unicode and UTF-8, if required (on Python2)
_native_to_unicode = (lambda s: s.decode("utf-8")) if six.PY2 else (lambda s: s)


# This set contains all letter and number characters.
_ALPHANUMERIC_CHAR_SET = set(
    six.unichr(i) for i in xrange(sys.maxunicode)
    if (unicodedata.category(six.unichr(i)).startswith("L") or
        unicodedata.category(six.unichr(i)).startswith("N")))


def encode(text):
  """Encode a unicode string as a list of tokens.

  Args:
    text: a unicode string
  Returns:
    a list of tokens as Unicode strings
  """
  if not text:
    return []
  ret = []
  token_start = 0
  # Classify each character in the input string
  is_alnum = [c in _ALPHANUMERIC_CHAR_SET for c in text]
  for pos in xrange(1, len(text)):
    if is_alnum[pos] != is_alnum[pos - 1]:
      token = text[token_start:pos]
      if token != u" " or token_start == 0:
        ret.append(token)
      token_start = pos
  final_token = text[token_start:]
  ret.append(final_token)
  return ret


def decode(tokens):
  """Decode a list of tokens to a unicode string.

  Args:
    tokens: a list of Unicode strings
  Returns:
    a unicode string
  """
  token_is_alnum = [t[0] in _ALPHANUMERIC_CHAR_SET for t in tokens]
  ret = []
  for i, token in enumerate(tokens):
    if i > 0 and token_is_alnum[i - 1] and token_is_alnum[i]:
      ret.append(u" ")
    ret.append(token)
  return "".join(ret)


if __name__ == "__main__":
    # python 2/3 compatibility
    import codecs
    if sys.version_info < (3, 0):
        sys.stderr = codecs.getwriter('UTF-8')(sys.stderr)
        sys.stdout = codecs.getwriter('UTF-8')(sys.stdout)
        #sys.stdin = codecs.getreader('UTF-8')(sys.stdin)
    else:
        sys.stderr = codecs.getwriter('UTF-8')(sys.stderr.buffer)
        sys.stdout = codecs.getwriter('UTF-8')(sys.stdout.buffer)
        #sys.stdin = codecs.getreader('UTF-8')(sys.stdin.buffer)
    for line in sys.stdin:
        line.strip()
        print(' '.join(encode(line)), '\n')
