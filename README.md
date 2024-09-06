# MetaMosaic: Automated Metadata Generator for Digital Images

MetaMosaic is a research-focused repository aimed at processing undigitized images from the Digital Repository at Northeastern University. This project leverages Google Gemini's computer vision and large language model (LLM) capabilities to generate titles, abstracts, and subjects for images, contributing to the metadata used in library archives.

This project is currently in the research phase but is planned for future integration into the Northeastern Digital Repository Services pipeline.

**LINK TO LLM TESTING SPREADSHEET: (https://docs.google.com/spreadsheets/d/1R5ee1EAB3jAFGcf7yF1zcKy2gPfhhpjEfJ12hB3jQ3M/edit?usp=sharing)**

## Gemini - link to Gemini_Prototype_Report
### Features

- **Image Processing:** Converts `.tif` images to `.jpeg` format (complying with DRS image standards) with reduced quality to optimize for generative models.
- **Automated Metadata Generation:** Generates transcriptions, titles, and abstracts for images using Google Gemini's advanced AI models.
- **Detail Extraction:** Extracts key metadata such as photographer name, dates, and raw transcriptions from image text. This step will be soon integrated into a database that will allow another script to verify if images are under Northeastern's copyright jurisdiction. 

### How It Works

1. **Image Conversion:** The script processes `.tif` images and converts them to `.jpeg` format, reducing quality for API processing optimization.
2. **Transcription:** The back of the photo is processed to generate a raw transcription using Google Gemini's LLM.
3. **Detail Extraction:** Key metadata like photographer name, dates, and raw transcription is extracted from the generated text.
4. **Title Generation:** The script generates a descriptive title for the image based on its content and extracted metadata.
5. **Abstract Generation:** Finally, an abstract is generated to summarize the context and content of the image.


