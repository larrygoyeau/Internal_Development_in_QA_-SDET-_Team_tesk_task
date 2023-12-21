import os
import shutil
import time
import argparse
import logging
from hashlib import md5

def get_file_md5(filename):
    hash_md5 = md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def synchronize_folders(source, replica):
    for src_dir, _, files in os.walk(source):
        dst_dir = src_dir.replace(source, replica, 1)

        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
            logging.info(f"Created directory '{dst_dir}' in replica.")

        for file in files:
            src_file = os.path.join(src_dir, file)
            dst_file = os.path.join(dst_dir, file)

            if not os.path.exists(dst_file) or get_file_md5(src_file) != get_file_md5(dst_file):
                shutil.copy2(src_file, dst_file)
                logging.info(f"Copied or updated '{src_file}' to '{dst_file}'.")

    for replica_dir, _, files in os.walk(replica):
        src_dir = replica_dir.replace(replica, source, 1)

        if not os.path.exists(src_dir):
            shutil.rmtree(replica_dir)
            logging.info(f"Deleted directory '{replica_dir}' from replica.")
            continue

        for file in files:
            src_file = os.path.join(src_dir, file)
            dst_file = os.path.join(replica_dir, file)

            if not os.path.exists(src_file):
                os.remove(dst_file)
                logging.info(f"Deleted '{dst_file}' from replica.")

def main():
    parser = argparse.ArgumentParser(description="Synchronize two folders.")
    parser.add_argument("source", help="Source folder path")
    parser.add_argument("replica", help="Replica folder path")
    parser.add_argument("interval", type=int, help="Synchronization interval in seconds")
    parser.add_argument("logfile", help="Log file path")
    args = parser.parse_args()

    logging.basicConfig(filename=args.logfile, level=logging.INFO, format='%(asctime)s - %(message)s')

    while True:
        synchronize_folders(args.source, args.replica)
        time.sleep(args.interval)

if __name__ == "__main__":
    main()
