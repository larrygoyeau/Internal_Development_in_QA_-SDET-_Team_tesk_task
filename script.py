import os
import shutil
import time
import argparse
import logging
from hashlib import md5

def calculate_md5_checksum(file_path):
    hash_md5 = md5()
    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def synchronize_directories(source_directory, replica_directory):
    # Synchronize files from source to replica
    for source_subdir, _, source_files in os.walk(source_directory):
        corresponding_replica_subdir = source_subdir.replace(source_directory, replica_directory, 1)

        if not os.path.exists(corresponding_replica_subdir):
            os.makedirs(corresponding_replica_subdir)
            logging.info(f"Created directory '{corresponding_replica_subdir}' in replica.")

        for file_name in source_files:
            source_file_path = os.path.join(source_subdir, file_name)
            replica_file_path = os.path.join(corresponding_replica_subdir, file_name)

            if (not os.path.exists(replica_file_path) or 
                calculate_md5_checksum(source_file_path) != calculate_md5_checksum(replica_file_path)):
                shutil.copy2(source_file_path, replica_file_path)
                logging.info(f"Copied or updated '{source_file_path}' to '{replica_file_path}'.")

    # Remove extra files and directories from replica
    for replica_subdir, _, replica_files in os.walk(replica_directory, topdown=False):
        corresponding_source_subdir = replica_subdir.replace(replica_directory, source_directory, 1)

        if not os.path.exists(corresponding_source_subdir):
            shutil.rmtree(replica_subdir)
            logging.info(f"Deleted directory '{replica_subdir}' from replica.")
            continue

        for file_name in replica_files:
            source_file_path = os.path.join(corresponding_source_subdir, file_name)
            replica_file_path = os.path.join(replica_subdir, file_name)

            if not os.path.exists(source_file_path):
                os.remove(replica_file_path)
                logging.info(f"Deleted '{replica_file_path}' from replica.")

def main():
    argument_parser = argparse.ArgumentParser(description="Synchronize two directories.")
    argument_parser.add_argument("source_directory", help="Path to the source directory")
    argument_parser.add_argument("replica_directory", help="Path to the replica directory")
    argument_parser.add_argument("sync_interval_seconds", type=int, help="Synchronization interval in seconds")
    argument_parser.add_argument("log_file_path", help="Path to the log file")
    args = argument_parser.parse_args()

    logging.basicConfig(filename=args.log_file_path, level=logging.INFO, format='%(asctime)s - %(message)s')

    while True:
        synchronize_directories(args.source_directory, args.replica_directory)
        time.sleep(args.sync_interval_seconds)

if __name__ == "__main__":
    main()
