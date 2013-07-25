#!/usr/bin/gawk -f
{
	if( $1 ~ /.py/ )
		plotcommand=$0
	else
		if( $0 ~ "[a-zA-Z0-9]+" )
		system(plotcommand" "$0)
}
