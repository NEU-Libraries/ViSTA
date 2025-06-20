#!/usr/bin/python
import sys
sys.path.append("/home/ec2-user/ViSTA_System")

from Image_Processors.gemini_image_processor import GeminiImageProcessor
from Transcription_Models.gemini_transcription_model import GeminiTranscriptionModel
from Image_Description_Models.gemini_image_description_model import GeminiImageDescriptionModel
from Metadata_Exporters.metadata_exporter import MetadataExporter
from Metadata_Exporters.metadata import Metadata
from Metadata_Exporters.extended_metadata import ExtendedMetadata
from logger import Logger
from Token_Trackers.gemini_token_tracker import GeminiTokenTracker
import pandas as pd
from datetime import datetime
import os
from pathlib import Path

# environment variable paths (on server)
INPUT_DIR = Path(os.environ["INPUT_DIR"])
OUTPUT_DIR = Path(os.environ["OUTPUT_DIR"])
LOG_DIR = Path(os.environ["LOG_DIR"])
CSV_DIR = Path(os.environ["CSV_DIR"])

def load_manifest(manifest):
    """
    Load the given manifest file
    :param manifest: manifest file.xlsx
    :return: manifest file as a DataFrame
    """
    manifest_dataframe = pd.read_excel(manifest)
    manifest_dataframe['Last Item'] = manifest_dataframe['Last Item'].fillna(False).astype(bool)
    return manifest_dataframe

def process_manifest_images(context, manifest, image_directory, generate_metadata):
    """
    Process images from a manifest file.
    Handles front-back and front-only cases.
    :param manifest (DataFrame): DataFrame containing the manifest file
    :param image_directory: Path to the directory containing the images
    :param generate_metadata: Lambda function to generate the metadata
    :return: N/A. Once processed, all metadata will be exported to a csv file
    """

    manifest = manifest.sort_values(by=['File Name', 'Sequence'])

    front_image_path = ""
    back_image_path = None

    for _, row in manifest.iterrows():
        file_name = row['File Name'] # name of file being processed 
        sequence = row['Sequence'] # 1 if front image, 2 if back image
        last_item = row['Last Item'] # boolean, is it the last image?
        additional_context = row['Context'] # place to add info about the image for the gemini prompt
        
        # if there's universal context for all images in the batch, it's added to the prompt here
        if not pd.isna(additional_context): # checking that something was added
            add_info = "The following info is context manually added by the librarian. This information should be prioritized over the transcription as it's more accurate:"
            additional_context = add_info + additional_context + ", " + context
        
        image_path = f"{image_directory}/{file_name}"
        
        if sequence == 1:  # front image
            front_image_path = image_path
        elif sequence == 2:  # back image
            back_image_path = image_path


        # process front-back pair or single front image if it is the last item
        if last_item:
            if back_image_path:
                generate_metadata(additional_context, front_image_path, back_image_path)
                # reset paths for next group
                front_image_path = ""
                back_image_path = ""
            else:
                generate_metadata(additional_context, front_image_path)
                # reset paths for next group
                front_image_path = ""
                back_image_path = ""

def generate_metadata(additional_context, image_front_path, image_processor, transcription_model,image_description_model, metadata_exporter, csv_file, token_tracker, logger, log_file_path, image_back_path=None):
    """
    Generates metadata for a single image and writes it to a csv file
    Works with either a single image, or an image_front/back pairing
    :param additional_context: additional context to enhance transcription results
    :param image_front_path: path to the image
    :param image_processor: ImageProcessor object to process image @ image_front_path
    :param transcription_model: TranscriptionModel object to generate a Transcription (object)
    :param image_description_model: ImageDescriptionModel object to generate title and abstract
    :param metadata_exporter: MetadataExporter object to write resulting Metadata object to csv file
    :param csv_file: The csv file you want to append the Metadata to
    :param token_tracker: TokenTracker object to track the tokens used to generate the metadata
    :param logger: Logger object to log the start/end times of each run through
    :param log_file_path: path to the log file
    :param image_back_path: Optional parameter that contains the Path to the image back if necessary
    :return: N/A. Results are written to a csv file
    """
    process_start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    error_message = ""

    try:
        # Process front image
        image_front = image_processor.process_image(image_front_path)
        context = ""
        transcription = None

        # Process back image and transcription if provided
        if image_back_path:
            image_back = image_processor.process_image(image_back_path)
            transcription = transcription_model.generate_transcription(image_back)
            context = transcription.transcription
            print(context)

        # Add context and additional context (if exist)
        if not pd.isna(additional_context):
            context = context + ", " + additional_context

        # Generate title and abstract
        title = image_description_model.generate_title(image_front, context)
        abstract = image_description_model.generate_abstract(image_front, context)

        # Create Metadata object
        metadata = Metadata(image_front.display_name, title, abstract, token_tracker)
        if image_back_path:
            metadata = ExtendedMetadata(image_front.display_name, title, abstract, transcription, token_tracker)

        # Write metadata to CSV
        metadata_exporter.write_to_csv(metadata, csv_file)

        # Reset token tracker
        token_tracker.reset()

    except Exception as e:
        # Capture error message
        error_message = str(e)
        logger.append_entry(log_file_path, image_front_path, process_start_time,
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"), error_message)
        raise  # Re-raise the exception after logging

    process_end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Log successful process completion
    if not error_message:
        logger.append_entry(log_file_path, image_front_path, process_start_time, process_end_time, error_message)


def main():
    # Ask for the image_directory they want to process
    # while loop that prompts users to keep re-entering folder name until a valid (existing) one is entered
    while True:
        image_batch_name = input("Name of image batch directory uploaded to the test-batches directory that you want to be processed: ")
        image_directory = f"../Test-Batches/{image_batch_name}"
    
        if os.path.isdir(image_directory):
            break  # Valid directory, exit loop
        print(f"'{image_batch_name}' does not exist in ../input folder. Please try again.")

    manifest = load_manifest(f"{image_directory}/manifest.xlsx")

    output_csv = f"{image_batch_name}_gemini_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"

    # Get Any Additional Context they want Added
    context = input("Any additional context to add to the prompt of all of these images? Enter nothing if not:")

    # Initialize image_processor
    image_processor = GeminiImageProcessor()

    # Initialize token tracker class
    token_tracker = GeminiTokenTracker()

    # Initialize logger and generate a log
    ViSTA_logger = Logger(LOG_DIR)
    
    log_file_path = ViSTA_logger.generate_log(f"{image_batch_name}_gemini_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_log.csv") 


    #Initialize transcription model
    transcription_prompt_file= "Prompts/Transcription_Prompts/transcription_step_one.txt"
    detail_extraction_prompt_file = "Prompts/Transcription_Prompts/transcription_step_two.txt"
    transcription_model = GeminiTranscriptionModel(transcription_prompt_file,detail_extraction_prompt_file,token_tracker)


    #Initialize image description model
    title_prompt_file = "Prompts/Title_Prompts/title_prompt.txt"
    abstract_prompt_file = "Prompts/Abstract_Prompts/abstract_prompt.txt"
    image_description_model = GeminiImageDescriptionModel(title_prompt_file, abstract_prompt_file,token_tracker)

    #Initialize metadata exporter class
    metadata_exporter = MetadataExporter()

    #ACTUAL PROCESSING FUNCTION AFTER MODULE CREATION STEPS
    process_manifest_images(
        context,
        manifest,
        image_directory,
        lambda additional_context, front, back=None: generate_metadata(
            additional_context, front, image_processor, transcription_model, image_description_model, metadata_exporter, output_csv  ,token_tracker, ViSTA_logger, log_file_path, back
        )
    )

if __name__ == '__main__':
    main()
