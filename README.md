# Vision-Informed Semantic Tagging and Annotator (ViSTA)

This repository is primarily aimed at processing undigitized images from the Digital Repository Service (DRS) at Northeastern University. This project leverages Gemini's VLM model (Flash 2.0) to tag images with key metadata (ie: titles, abstracts, and subjects), contributing to Northeastern's Digital Repository Archives.

This repository is open for use by anyone interested in metadata tagging and annotation, including but not limited to libraries, archives, and other literary organizations.

Below is a diagram illustrating how ViSTA currently runs
**[LINK TO ViSTA Pipeline](https://drive.google.com/file/d/1nGYczoj3l8fU7gh0cm3Bv9xO6-JgePxL/view?pli=1)**

### How It Works
1. **Additional Context**  Users can add info to accompany specific photos in the manifest file, or generally to all photos in a folder when prompted while running ViSTA. This information will be added to the prompt and given prioritization over transcription info.
2. **Image Pre-Processing** The system pre-processes images and converts them to `.jpeg` format for VLM use, adjusting quality to optimize for API Image upload constraints. 
3. **Transcription:** Some collections within the DRS (ie: Boston Globe) contain an additional side to each of the digitally stored photographs that possesses additional textual context about the photograph itself. ViSTA is capable of transcribing text off of the additional image to extract valuable context to support further metadata generation.
4. **Title and Abstract Generation:** The script generates descriptive titles and abstracts for the image based on its content as well as additional context.
5. **Tagging** The metadata generated is tagged to each image and exported into a given csv file, or can be exported into JSON format. 

### Contact
If you have any questions about ViSTA, you can reach out to Digital Production Services at Snell Library by emailing them: Library-DPS@northeastern.edu