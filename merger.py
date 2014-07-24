import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument( "input_file", action="store" )
parser.add_argument( "output_file", action="store" )
args = parser.parse_args()

in_file = open( args.input_file, "r" )
out_file = open( args.output_file, "r" )

input_content = in_file.read()
output_content = out_file.read()

in_file.close()
out_file.close()

input_json = json.loads( input_content )
output_json = json.loads( output_content )

for position in input_json:
    if not position in output_json:
        output_json[ position ] = []
    
    for player in input_json[ position ]:
        player_found = False
        for search_player in output_json[ position ]:
            if search_player[ "Player" ] == player[ "Player" ]:
                player_found = True
                break
        
        if not player_found:
            output_json[ position ].append( player )


out_file = open( args.output_file, "w" )
out_file.write( json.dumps( output_json, sort_keys=True, indent=4, separators=(',', ': ') ) )
out_file.close()
