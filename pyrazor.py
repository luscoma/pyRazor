"""The main library entry for pyrazor."""

__author__ = "Alex Lusco"

import logging

import lex
import razorview


def Parse(text, ignore_whitespace=False):
  """Creates a razorview from template text.

  Args:
    text: The template text to render
    ignore_whitespace: If true the renderer will strip whitespace at the
        beginning of each line in text.
  """
  return razorview.ParseView(text, ignore_whitespace)


def Render(text, model=None, ignore_whitespace=False):
  """Renders the template text using the given model

  Args:
    text: The template text to render
    model: The model object to pass to the view
    ignore_whitespace: If true the renderer will ignore whitespace.
  """
  view = Parse(text, ignore_whitespace)
  return view.Render(model)

