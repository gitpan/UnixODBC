#!/usr/local/bin/perl -w

use CGI;
use CGI::Carp qw(fatalsToBrowser);
use UnixODBC (':all');
use UnixODBC::BridgeServer;
# use Log::Agent;
use RPC::PlClient;

my $q = new CGI;
#my $dsnquery = $ENV{'QUERY_STRING_UNESCAPED'};
my $dsnquery = $ENV{'REQUEST_URI'};
my ($host, $dsn) = ($dsnquery =~ /hostdsn=(.*)--(.*)/);
$dsn =~ s/\+/ /g;

my $styleheader = <<END_OF_HEADER;
<!DOCTYPE html
	PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
	 "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en-US">
<head><title>Untitled Document</title>
<style type="text/css">
A {color: blue}
TEXTAREA {background-color: transparent}
DIV.dsnlist {margin-left: 2}
DIV.tablelist {margin-left: 4}
DIV.loginmsg {margin-left: 10}
</style>
</head>
END_OF_HEADER

no warnings;
my $form = <<ENDOFFORM;
<form action="/cgi-bin/datamanager.cgi" target="dsns">
 <table align="center" cellpadding="10">
  <tr>
   <td>
    <label>User Name:</label><br>
    <input type="text" name="username" value="$user"><br>
    <label>Password:</label><br>
    <input type="password" name="password" value="$password"><br>
    <label>Host Name:</label><br>
    <input type="text" name="host" value="$host"><br>
    <label>Data Source:</label><br>
    <input type="text" name="dsn" value="$dsn"><br>
  </td>
 </tr>
 <tr>
  <td>
    <center><input type="submit" name="submit" value="Log In"></center>
  </td>
 </tr>
</table>
</form>
ENDOFFORM
use warnings;

print $q -> header;
print $styleheader;
print qq|<body bgcolor="white" text="blue">\n|;
print qq|<center>|;
print qq|<h1><img src="/icons/odbc.gif" hspace="5">\n|;
print qq|Please log in:</h1>\n|;
print qq|</center>|;
print $form;
&endhtml;

sub endhtml {
    print $q -> end_html;
}
