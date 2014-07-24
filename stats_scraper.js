/*
http://fantasynews.cbssports.com/fantasyfootball/stats/weeklyprojections/QB/season
*/

var fileref=document.createElement('script')
fileref.setAttribute("type","text/javascript")
fileref.setAttribute("src", "//ajax.googleapis.com/ajax/libs/jquery/1.10.2/jquery.min.js")
document.getElementsByTagName("head")[0].appendChild(fileref)

var players = [ ]
var categories = [ ]
var columns = [ ]

$( ".data tr#special td" ).each( function( index, elem ) {
	var colspan = parseInt( $( elem ).attr( "colspan" ), 10 )
	var coltext = $( elem ).text()
	coltext = $.trim( coltext )
	for( var i = 0; i < colspan; i++ )
	{
		categories.push( coltext )
	}
});

$( ".data tr.label td a" ).each( function( index, elem ) {
	columns.push( $.trim( categories[ index ] + " " + $( elem ).html() ) )
});

$( ".data tr.row1" ).each( function( index, row ) {
	
	if( index != 0 )
	{
		var new_player = { }
		
		$( row ).children().each( function( index, column ) {
			new_player[ columns[ index ] ] = $( column ).text()
		});
		
		players.push( new_player )
	}
});

var new_json = {}
new_json[ $( "#position" ).val() ] = players

JSON.stringify( new_json );
