#!/usr/bin/python

import json
import os
import cmd
import difflib

def process_data( filename ):
    f = open( filename )
    contents = f.read()
    raw_player_data = json.loads( contents ) 
    f.close()

    player_fpts = []
    
    index = 0
    
    max_pts = {}
    min_pts = {}
    
    # Read in all player data from the external JSON file.
    # We'll also track the min and max fpts scores for
    # each position
    
    for position in raw_player_data:
        
        max_pts[ position ] = 0.0
        min_pts[ position ] = 65535.0
        
        for player in raw_player_data[ position ]:
            fpts_key = ""

            for key in player.keys():
                if "FPTS" in key or "fpts" in key:
                    fpts_key = key
                    break

            try:
                fpts = float( player[ fpts_key ] )
                
                if fpts > max_pts[ position ]:
                    max_pts[ position ] = fpts
                
                if fpts < min_pts[ position ]:
                    min_pts[ position ] = fpts
                
                player_fpts.append( {
                    "position" : position,
                    "name" : player[ "Player" ].strip(),
                    "fpts" : fpts,
                    "free" : True,
                    "index" : index
                } )
                index+=1
            except:
                pass
    
    # Now, lets post-process. We'll take the maximum and minimum score
    # production to give each option a 'quality' attribute specific to
    # their position
    
    for player in player_fpts:
        max = max_pts[ player[ "position" ] ]
        min = min_pts[ player[ "position" ] ]
        
        # Normalize fpts for the given position and store as 'quality'
        player[ "quality" ] = ( player[ "fpts" ] - min ) / ( max - min )
    
    # sorted is stable. that allows us to sort by fpts first, and then by quality. 
    # This way items will be sorted by quality, and then sorted by fpts within quality
    player_fpts = sorted( player_fpts, key=lambda player: player[ "fpts" ], reverse=True )
    player_fpts = sorted( player_fpts, key=lambda player: player[ "quality" ], reverse=True )
    return player_fpts

def get_display_string( player_data, nlines, showNRecords = True ):
    output = "{:<3} {:>3} {:<30} {:>6} {:>4}".format( "IDX", "POS", "Player", "FPTS", "QUAL" )
    output += os.linesep
    
    if nlines > len( player_data ):
        nlines = len( player_data )
    
    for i in range( 0, nlines ):
        player = player_data[ i ]
        output += "{:>03} {:>3} {:<30} {:>3.2f} {:>1.2f}".format( player["index"], player[ "position" ], player[ "name" ], player["fpts"], player[ "quality" ] )
        output += os.linesep
        
    if showNRecords:
        output += os.linesep
        output += "Total Records Found = " + str( len( player_data ) ) + os.linesep
    
    return output

class Roster:
    roster_template = {
        "QB" : 1,
        "RB" : 2,
        "WR" : 2,
        "TE" : 1,
        "flex" : 1,
        "DST" : 1,
        "K" : 1,
        "bench" : 9
    }
    
    def __init__(self):
        self.roster = {}
    
    def add_player_to_roster(self, player):
        
        if player[ "position" ] not in self.roster:
            self.roster[ player[ "position" ] ] = []
        
        self.roster[ player[ "position" ] ].append( player )
    
    def rm_player_from_roster(self, player):
        
        if player[ "position" ] not in self.roster:
            return
        
        self.roster[ player[ "position" ] ] = [ p for p in self.roster[ player[ "position" ] ] if p["index"] != player["index"] ]
        return
    
    def print_roster(self):
        for pos in self.roster:
            print get_display_string( self.roster[ pos ], 10, False )
    
    def picking_backups(self):
        if len( self.roster ) != 6:
            return False
        
        needed_qb = Roster.roster_template[ "QB" ] - len( self.roster[ "QB" ] )
        needed_rb = Roster.roster_template[ "RB" ] - len( self.roster[ "RB" ] )
        needed_wr = Roster.roster_template[ "WR" ] - len( self.roster[ "WR" ] )
        needed_te = Roster.roster_template[ "TE" ] - len( self.roster[ "TE" ] )
        needed_dst = Roster.roster_template[ "DST" ] - len( self.roster[ "DST" ] )
        needed_k = Roster.roster_template[ "K" ] - len( self.roster[ "K" ] )
        
        return ( needed_qb <= 0 and needed_rb <= 0 and needed_wr <= 0 and needed_te <= 0 and needed_dst <= 0 and needed_k <= 0 )
        
    def need_player(self, player):
        needed = Roster.roster_template[ player[ "position" ] ]
        
        if self.picking_backups():
            needed *= 2
        
        # check the flex position
        if player[ "position" ] == "RB" or player[ "position" ] == "WR":
            needed_rb = Roster.roster_template[ "RB" ]
            needed_wr = Roster.roster_template[ "WR" ]
            needed_flex = Roster.roster_template[ "flex" ]
            
            if "RB" in self.roster:
                needed_rb -= len( self.roster[ "RB" ] )
            
            if "WR" in self.roster:
                needed_rb -= len( self.roster[ "RB" ] )
            
            if needed_rb < 0:
                needed_flex -= abs( needed_rb )
                
            if needed_wr < 0:
                needed_flex -= abs( needed_wr )
            
            if needed_flex > 0:
                needed += needed_flex
        
        if player[ "position" ] in self.roster:
            needed -= len( self.roster[ player[ "position" ] ] )
        
        return needed > 0

class GrenadeShell(cmd.Cmd):
    intro = '''
                             /|
                             |@/
                            _/"
                          _/==\__
                         (==---==)              Bring
                      /%/_________\             Out
                     /#(_|_|_|_|_|_)            Thou
                    |#(_|_|_|_|_|_|_)           Holy
                    |#(|_|_|_|_|_|_|)           Hand
                    |#(_|_|_|_|_|_|_)           Grenade
                     \#(_|_|_|_|_|_)
                      \#|_|_|_|_|_/
                       '"-------"

Holy Hand Grenade Fantasy Football Draft Manager
Enter 'help' or '?' for a list of commands.
'''
    prompt = '=> '
    file = None
    
    def __init__( self ):
        cmd.Cmd.__init__( self )
        self.player_data = process_data( "data.txt" )
        self.roster = Roster()
    
    def do_top20(self,arg):
        try:
            data = [ p for p in self.player_data if p["free"] ]
            
            if arg.strip() != "":
                data = [ p for p in data if arg.lower() in p["position"].lower() ]
            else:
                data = [ p for p in data if self.roster.need_player( p ) ]
            
            print get_display_string( data, 20 )
        except Exception as err:
            print "{ERROR} " + str( err )
            print
    
    def help_top20(self):
        print 'Syntax: top20 <position (optional)>'
        print 'Prints the top20 picks based on the remaining free agents'
        print
    
    def do_search(self,arg):
        try:
            results = []
            
            for p in self.player_data:
                matcher = difflib.SequenceMatcher( a=arg, b=p[ "name" ] )
                p[ "score" ] = matcher.ratio()
            
            data = sorted( self.player_data, key=lambda x: x["score"], reverse=True )
            
            print get_display_string( data, 10 )
        except Exception as err:
            print "{ERROR} " + str( err )
            print
    
    def help_search(self):
        print 'Syntax: search <player name>'
        print 'Search for a player by their name or a portion of their name'
        print
    
    def do_taken(self,arg):
        try:
            for p in self.player_data:
                if int( p["index"] ) == int( arg ):
                    s = raw_input( "Mark " + p["name"] + " as taken? [y/n]" )
                    if s == 'y':
                        p[ "free" ] = False
                    break
        except Exception as err:
            print "{ERROR} " + str( err )
            print
    
    def help_taken(self):
        print 'Syntax: taken <player index>'
        print 'Mark a player as taken by another team'
        print
        
    def do_available(self,arg):
        try:
            for p in self.player_data:
                if int( p["index"] ) == int( arg ):
                    s = raw_input( "Mark " + p["name"] + " as taken? [y/n]" )
                    if s == 'y':
                        p[ "free" ] = True
                    break
        except Exception as err:
            print "{ERROR} " + str( err )
            print
    
    def help_available(self):
        print 'Syntax: available <player index>'
        print 'Mark a player as available for drafting'
        print
    
    def do_addRoster(self,arg):
        try:
            for p in self.player_data:
                if int( p["index"] ) == int( arg ):
                    s = raw_input( "Remove " + p["name"] + " from your roster ? [y/n]" )
                    if s == 'y':
                        self.roster.add_player_to_roster( p )
                        p[ "free" ] = False
                    break
        except Exception as err:
            print "{ERROR} " + str( err )
            print
           
    def help_addRoster(self):
        print 'Syntax: addRoster <player index>'
        print 'Add a player to your roster'
        print
        
    def do_rmRoster(self,arg):
        try:
            for p in self.player_data:
                if int( p["index"] ) == int( arg ):
                    s = raw_input( "Add " + p["name"] + " to your roster ? [y/n]" )
                    if s == 'y':
                        self.roster.rm_player_from_roster( p )
                        p[ "free" ] = True
                    break
        except Exception as err:
            print "{ERROR} " + str( err )
            print
    
    def help_rmRoster(self):
        print 'Syntax: rmRoster <player index>'
        print 'Remove a player from your roster'
        print
    
    def do_showRoster(self,arg):
        try:
            self.roster.print_roster()
        except Exception as err:
            print "{ERROR} " + str( err )
            print
    
    def help_showRoster(self):
        print 'Syntax: showRoster'
        print 'Show your current roster'
    
    def do_exit(self,arg):
        try:
            s = raw_input( "Are you sure? [y/n] " )
            if s == "y":
                return True
        except Exception as err:
            print "{ERROR} " + str( err )
            print
    
    def help_exit(self):
        print 'Syntax: exit'
        print 'Exit the holy hand grenade shell'
        print
        
if __name__ == "__main__":
    GrenadeShell().cmdloop()

