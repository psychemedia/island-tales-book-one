#!/bin/bash
# buildcovers

# Check for project name argument
if [ -z "$1" ]; then
  echo "Usage: ./buildcovers <projectname>"
  exit 1
fi

PROJECT="$1"
SRC_DIR="./$PROJECT"
BUILD_DIR="$SRC_DIR/_build"

# Create build directory if it doesn't exist
mkdir -p "$BUILD_DIR"

# List of TeX files to compile
TEX_FILES=(
  "${PROJECT}-new-cover-kdp.tex"
  "${PROJECT}-new-cover-kdp-ebook.tex"
)

# Compile each TeX file twice
for TEX in "${TEX_FILES[@]}"; do
  echo "Compiling $TEX (pass 1)..."
  xelatex -output-directory="$BUILD_DIR" "$SRC_DIR/$TEX"

  echo "Compiling $TEX (pass 2)..."
  xelatex -output-directory="$BUILD_DIR" "$SRC_DIR/$TEX"

  # Move PDF from build to source
  PDF_FILE="${TEX%.tex}.pdf"
  if [ -f "$BUILD_DIR/$PDF_FILE" ]; then
    mv "$BUILD_DIR/$PDF_FILE" "$SRC_DIR/$PDF_FILE"
  else
    echo "Warning: $PDF_FILE not found in $BUILD_DIR!"
  fi
done

# Convert PDFs to JPGs in source folder
for TEX in "${TEX_FILES[@]}"; do
  PDF_FILE="${TEX%.tex}.pdf"
  INPUT_PDF="$SRC_DIR/$PDF_FILE"
  OUTPUT_JPG="$SRC_DIR/${PDF_FILE%.pdf}.jpg"

  if [ -f "$INPUT_PDF" ]; then
    echo "Converting $PDF_FILE to JPG..."
    magick -density 300 "$INPUT_PDF" "$OUTPUT_JPG"
  else
    echo "Warning: $INPUT_PDF not found for conversion!"
  fi
done

echo "Build complete. PDFs and JPGs are in $SRC_DIR, intermediate files in $BUILD_DIR."
