#!/usr/bin/awk -f
BEGIN {
 nrows = 0;
 FS =" ";
}
{
 if ($1 ~ /[0-9]/) 
  {
  if ($1 != nrows) {
   print "";
   }
  nrows=$1;
  print $1" "$2" "$9*1e-9;
  } 
}

