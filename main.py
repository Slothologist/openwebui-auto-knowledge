from watchdog.observers import Observer
import os
import sys
import yaml
import time
from src import KnowledgeSync

# Monitor directory
if __name__ == "__main__":
    config = None

    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    else:
        print('Usage: main.py <path_to_config_file>')
        exit(0)

    # check for config file
    if os.path.exists(config_path):
        config = yaml.safe_load(open(config_path))
        print('Config is:', config)
    else:
        print('Config file not found, creating example config. Be sure to modify it!')
        copy = 'cp openwebui-auto-knowledge/config.yaml ' + config_path
        output = os.system(copy)
        if output:
            print('Config file could not be created! Check watch folder ownership/ permissions. The user with UID, GID defined in docker compose needs write permission.')
        exit(0)

    sync_handler = KnowledgeSync(config)
    observer = Observer()
    observer.schedule(sync_handler, config['watch_directory'], recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()