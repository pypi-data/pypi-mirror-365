import json
import logging
import os

import hcl2

from .bedrock_client import aws_bedrock
from .output_writer import output_md, validate_output_json
from .utils import ensure_directory_exists, measure_time
from .logger_config import get_logger, log_exception

logger = get_logger("file_processor")


def run_hcl_file_workflow(file_path: str, config: dict, system_config: dict) -> None:
    """
    Process a hcl file and generate a JSON output.
    Args:
        file_path (str): Path to the hcl file.
        config (dict): Configuration for processing.
        system_config (dict): System configuration.
    Raises:
        FileNotFoundError: If the hcl file does not exist or is empty.
        ValueError: If the hcl file cannot be parsed.
    """
    with measure_time(f"HCL file processing: {os.path.basename(file_path)}", logger):
        locals_str = read_local_files(config["input"]["local_files"])
        hcl_raw, _ = read_tf_file(file_path)
        if hcl_raw is None:
            logger.warning(f"File not found or empty: {file_path}")
            raise FileNotFoundError(f"File not found or empty: {file_path}")
        if config["input"]["modules"].get("enabled", True):
            modules_raw, _ = read_tf_file(config["input"]["modules"]["path"])
        else:
            modules_raw = None
        try:
            resource_dict = hcl2.loads(hcl_raw)
        except Exception as e:
            log_exception(logger, e, f"Error parsing HCL file {file_path}")
            raise
        try:
            combined_str = f"{locals_str}\n ---resource hcl \n {resource_dict}\n"
            logger.debug(f"Combined string:\n {combined_str}")
            output_str = aws_bedrock(combined_str, modules_raw, config, system_config)
            logger.debug(f"Output string:\n {output_str}")
            validated_output = validate_output_json(
                output_str, config["bedrock"]["output_json"]
            )
            logger.debug(f"Validated output:\n {validated_output}")
            ensure_directory_exists(config["output"]["json_path"])
            try:
                # TODO: Need to consider creating a temporary file.
                with open(config["output"]["json_path"], "w", encoding="utf-8") as f:
                    json.dump(validated_output, f, ensure_ascii=False, indent=4)
                    logger.info(f"Successfully wrote JSON output to {config['output']['json_path']}")
            except Exception as e:
                log_exception(logger, e, "Error writing JSON output")
                raise
            logger.info(f"Successfully processed file: {file_path}")
            tf_extension = system_config["constants"]["file_processing"]["terraform_extension"]
            output_md(os.path.basename(file_path).replace(tf_extension, ""), config)
        except json.decoder.JSONDecodeError:
            logger.error("Prompt too large or malformed JSON, retrying in chunks...")
            hcl_output = []
            # TODO: Need to review implementation
            if config["input"]["failback"]["enabled"]:
                search_resource = system_config["constants"]["file_processing"]["default_search_resource"]
                module_name = get_modules_name(resource_dict, search_resource)
                if config["input"]["failback"]["type"] == "resource":
                    # TODO: Not yet guaranteed to work
                    resources = resource_dict["resource"]
                else:
                    resources = resource_dict["module"][0][module_name][
                        config["input"]["failback"]["options"]["target"]
                    ]
                try:
                    for resource in resources:
                        combined_str = f"{locals_str}\n{resource}\n"
                        partial_output = aws_bedrock(
                            combined_str, modules_raw, config, system_config
                        )
                        validated_partial = validate_output_json(
                            partial_output, config["bedrock"]["output_json"]
                        )
                        hcl_output.append(validated_partial)
                except Exception as e:
                    log_exception(logger, e, "Error processing resource chunk")
                    pass
                flattened_list = []
                for json_obj in hcl_output:
                    try:
                        flattened_list.extend(json_obj)
                    except Exception as e:
                        log_exception(logger, e, f"Error extending flattened list with: {json_obj}")

                with open(config["output"]["json_path"], "w", encoding="utf-8") as f:
                    json.dump(flattened_list, f, ensure_ascii=False, indent=4)
                tf_extension = system_config["constants"]["file_processing"]["terraform_extension"]
                output_md(os.path.basename(file_path).replace(tf_extension, ""), config)
            else:
                logger.error("Failback is not enabled, skipping chunk processing.")
                if not logger.isEnabledFor(logging.DEBUG):
                    return
                else:
                    raise


def read_tf_file(file_path: str) -> tuple[str, str]:
    """
    Read a Terraform file and return its content.
    Args:
        file_path (str): Path to the Terraform file.
    Returns:
        str: Content of the Terraform file.
        str: Directory of the Terraform file.
    Raises:
        FileNotFoundError: If the file does not exist.
    """
    if os.path.exists(file_path):
        with measure_time(f"Reading Terraform file: {os.path.basename(file_path)}", logger):
            with open(file_path, "r") as f:
                content = f.read()
                file_size_kb = len(content) / 1024
                logger.debug(f"File size: {file_size_kb:.2f} KB")
                return content, os.path.dirname(file_path)
    raise FileNotFoundError(f"File not found: {file_path}")


def read_local_files(local_files: list) -> str:
    """
    Read local files and return their content.
    Args:
        local_files (list): List of local files to read.
    Returns:
        str: Content of the local files.
    Raises:
        FileNotFoundError: If any local file does not exist.
    """
    if not local_files:
        logger.debug("No local files to read")
        return ""
        
    with measure_time(f"reading {len(local_files)} local files", logger):
        result = []
        total_size_kb = 0
        for entry in local_files:
            for env, path in entry.items():
                if os.path.exists(path):
                    try:
                        with open(path, "r", encoding="utf-8") as f:
                            content = f.read()
                            file_size_kb = len(content) / 1024
                            total_size_kb += file_size_kb
                            logger.debug(f"Local file {os.path.basename(path)}: {file_size_kb:.2f} KB")
                            result.append(f"{env}\n---\n{hcl2.loads(content)}\n")
                    except Exception as e:
                        log_exception(logger, e, f"Error reading local file {path}")
                        raise
                else:
                    raise FileNotFoundError(f"Local file not found: {path}")
        logger.debug(f"Total local files size: {total_size_kb:.2f} KB")
        return "\n".join(result)


def get_modules_name(resource_dict: dict, search_resource: str = None) -> str:
    """
    Extract the module name from the hcl dictionary.
    Args:
        hcl_dict (dict): The hcl dictionary.
    Returns:
        str: The module name.
    Raises:
        ValueError: If no module name is found.
    """
    for resource_name, resource_data in resource_dict.get("module", [{}])[0].items():
        if search_resource in resource_data:
            logger.info(f"resource_name: {resource_name}")
            return resource_name
    raise ValueError("No module name found in hcl_dict")
