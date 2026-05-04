#!/bin/bash
# compress_pdf.sh — Compress and flatten a PDF for Amazon KDP.
#
# Usage:
#   ./compress_pdf.sh input.pdf [output.pdf]
#
# If output.pdf is omitted, creates input_compressed.pdf
# Requires: ghostscript (brew install ghostscript)
#
# KDP recommended settings:
#   300 dpi colour images, 600 dpi mono, no encryption, no JavaScript,
#   all fonts embedded, transparency flattened.

set -e

INPUT="$1"
OUTPUT="${2:-}"

if [[ -z "$INPUT" ]]; then
  echo "Usage: $0 input.pdf [output.pdf]"
  exit 1
fi

if [[ ! -f "$INPUT" ]]; then
  echo "ERROR: File not found: $INPUT"
  exit 1
fi

if [[ -z "$OUTPUT" ]]; then
  BASE="${INPUT%.pdf}"
  OUTPUT="${BASE}_compressed.pdf"
fi

GS=$(which gs 2>/dev/null || which gswin64c 2>/dev/null)
if [[ -z "$GS" ]]; then
  echo "ERROR: ghostscript not found. Install with: brew install ghostscript"
  exit 1
fi

echo "Input:  $INPUT  ($(du -h "$INPUT" | cut -f1))"
echo "Output: $OUTPUT"
echo "Compressing..."

"$GS" \
  -sDEVICE=pdfwrite \
  -dCompatibilityLevel=1.4 \
  -dPDFSETTINGS=/printer \
  -dNOPAUSE -dQUIET -dBATCH \
  -dColorImageResolution=300 \
  -dGrayImageResolution=300 \
  -dMonoImageResolution=600 \
  -dColorImageDownsampleType=/Bicubic \
  -dGrayImageDownsampleType=/Bicubic \
  -dDownsampleColorImages=true \
  -dDownsampleGrayImages=true \
  -dFastWebView=false \
  -dEmbedAllFonts=true \
  -dSubsetFonts=true \
  -dCompressFonts=true \
  "-sOutputFile=$OUTPUT" \
  "$INPUT"

echo ""
echo "Done!"
echo "Input:  $(du -h "$INPUT"  | cut -f1)"
echo "Output: $(du -h "$OUTPUT" | cut -f1)"
