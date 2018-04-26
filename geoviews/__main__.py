import argparse
import inspect

from . import __version__, examples

def install_examples(args):
    """Install examples at the supplied path."""
    examples(args.path, args.include_data, args.verbose)

def main(args=None):
    parser = argparse.ArgumentParser(description="GeoViews commands")
    parser.add_argument('--version', action='version', version='%(prog)s '+__version__)
    
    subparsers = parser.add_subparsers(title='available commands')

    eg_parser = subparsers.add_parser('install_examples', help=inspect.getdoc(install_examples))
    eg_parser.set_defaults(func=install_examples)
    eg_parser.add_argument('--path',type=str,help='where to install examples',default='geoviews-examples')
    eg_parser.add_argument('--include-data',action='store_true',help='Also download sample data') 
    eg_parser.add_argument('-v', '--verbose', action='count', default=0)
    
    args = parser.parse_args()

    if hasattr(args,'func'):
        args.func(args)
    else:
        parser.error("must supply command to run") 

if __name__ == "__main__":
    main()
