

import os
import configparser


class ConfigManager:
    
    def __init__(self) -> None: 
        self.current_directory = os.path.dirname(__file__)
        
    def read_config(self, conf_type, section=False):
        config = configparser.ConfigParser(allow_no_value=True)
        config_file = self.config.read(os.path.join(self.current_directory, "../config/conf.cfg"))
        dict_conf_type = {
            "config_file": config_file
        }
        
        if section:
            config.read(dict_conf_type[conf_type])
            dict_conf = config._section[section]
        else:
            config.read(dict_conf_type[conf_type])
            for section_key, section_value in config._section.items():
                for k, v in section_value.items():
                    dict_conf[f"{section_key}_{k}"] = v.strip()
        
        return dict_conf