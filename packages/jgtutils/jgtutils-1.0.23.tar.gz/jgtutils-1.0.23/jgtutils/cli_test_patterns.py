import os

import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import jgtcommon

def parse_args():
    parser = jgtcommon.new_parser("Timeframe Test settings","Test loading custom timeframes from settings",enable_specified_settings=True)
    #parser=jgtcommon.add_settings_argument(parser)
    #parser=jgtcommon._preload_settings_from_args(parser)
    
    parser= jgtcommon.add_patterns_arguments(parser)
    parser=jgtcommon.add_timeframe_standalone_argument(parser)
    args = jgtcommon.parse_args(parser)
    return args

def main():
    args = parse_args()
    #settings = jgtcommon.load_settings(args)
    print("Settings loaded:")
    print(jgtcommon.settings)
    
if __name__ == '__main__':
    main()
    
