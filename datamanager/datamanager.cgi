#!/usr/local/bin/perl

use CGI;
use CGI::Carp qw(fatalsToBrowser);
use UnixODBC (':all');
use UnixODBC::BridgeServer;
use RPC::PlClient;

#
# If you change the subdirectory where the data manager SHTML, HTML,
# and graphics files are located, change the value of $folder here.
# 
my $folder='datamanager';


my $loginfile = '/usr/local/etc/odbclogins'; # File that contains login data.
my %peers; # Peer host login data from /usr/local/etc/odbclogins

my $peerport = 9999;
my $loginmsg = '';

&readlogins;

my $q = new CGI;
my @params = $q -> param;

my $server_addr = $ENV{SERVER_ADDR};


#
# If generating page from the the login screen.
my @dsnlogin = $q -> param;
# Parameters for remote host logins.
my ($username, $password, $host, $dsn);
# Parameters for remote DBMS logins.
my ($dsnuser, $dsnpwd);
# Temporary strings for URL parameter writing.
my ($datasource, $dsnparam);
# Error return value for connect and show tables query
my $connecterr;
# List of table names
my @tablenames;

# Hosts and child nodes are displayed in order of @dsns array.
my @dsns;
my @serverdsns;
my @servers;

my $noconnectstr = 'noconnect';

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

if ($#dsnlogin != -1) {
    $dsnuser = $q -> param('username');
    $dsnpwd = $q -> param('password');
    $host = $q -> param ('host');
    $dsn = $q -> param ('dsn');
    my ($peeruser, $peerpwd) = split /::/, $peers{$host};
    $connecterr = &gettablenames ($host, $dsn, $dsnuser, $dsnpwd);
    if (! length $connecterr) {
	$loginmsg = 'Connected to data source <i>' . $dsn .
	    '</i> on host <i>' . $host . 
	    '</i> as user <i>' . $dsnuser . '.</i>';
    } else {
	$loginmsg = 'Login error on host <i>'. $host . '.</i>: '. 
	    $connecterr;
    }
} else {
    $loginmsg = 'Not logged in.';
}

foreach my $peeraddr (keys %peers) {
    my ($peerusername, $peerpassword) = split /::/, $peers{$peeraddr};
    my $client =
	eval { RPC::PlClient->new('peeraddr' => $peeraddr,
                          'peerport' => $peerport,
                          'application' => 'RPC::PlServer',
                          'version' => $UnixODBC::VERSION,
                          'user' => $peerusername,
                          'password' => $peerpassword) };

    if (not defined $client) {
	push @servers, ("$peeraddr - $noconnectstr");
	next;
    }

    my $c = $client -> ClientObject ('BridgeAPI', 'new');

    if (ref $c ne 'RPC::PlClient::Object::BridgeAPI' ) {
	print qq|Error could not create UnixODBC.pm client object.<br>|;
	push @servers, ("$peeraddr - $noconnectstr");
	next;
    }

    @serverdsns = &remotedsn ($c);
    foreach my $d (@serverdsns) {
	push @dsns, ("$peeraddr - $d");
    }
    push @servers, ($peeraddr);
}

print $q -> header;
# This gets around the <?xml? DTD header in CGI.pm
print $styleheader;
print qq|<body bgcolor="white" text="blue">\n|;
print qq|<img src="/icons/odbc.gif" hspace="5" height = "32" width="32">\n|;
print qq|<font size="5">Data Sources</font><p>\n|;

print qq|<div class="loginmsg">|;
print qq|$loginmsg<p>|;
print qq|</div>|;

foreach my $s (@servers) {
    if ($s =~ m"$noconnectstr") { # Couldn't create client object
                                  # so print no-term and go to next server.
	local ($servername) = ($s =~ m"(.*) - $noconnectstr");
	print qq|   <a href="dsns.shtml">\n|;
	print qq|     <img src="/icons/term-no.gif" border="0" |;
	print qq|     align="middle" hspace="10"><font size="4">\n|;
	print qq|     $servername</font>\n|;
	print qq|   </a><br>\n|;
	next;
    }
    print qq|   <a href="dsns.shtml">\n|;
    print qq|     <img src="/icons/terminal.gif" border="0" |;
    print qq|     align="middle" hspace="10"><font size="4">$s</font>\n|;
    print qq|   </a><br>\n|;

    foreach my $d (@dsns) {
	if ($d =~ m"$s") {
	    ($datasource) = ($d =~ m".* - (.*)");
	    $dsnparam = $datasource;
	    $dsnparam =~ s/ /\+/g;
	    print qq|<div class="dsnlist">\n|;
	    print qq|<a href="http://$server_addr/$folder/|;
	    print qq|odbclogin.shtml?hostdsn=$s--$dsnparam" |;
	    print qq| target="main">\n|;
	    print qq|<img src="/icons/dsn.gif" border="0" |;
	    print qq| align="middle" hspace="10">\n|;
	    print qq|$datasource</a><br>\n|;
	    print qq|</div>\n|;
	}
	if ( ($s =~ m"$host") and ($d =~ m"$dsn") ) {
	    print qq|<div class="tablelist">|;
	    foreach my $table (@tablenames) {
		print qq|<a href="http://$server_addr/$folder/|;
                print qq|tables.shtml?hostdsntable=$s--$dsnparam--$table&username=$dsnuser&password=$dsnpwd" |;
		print qq| target="main">\n|;
		print qq|<img src="/icons/table.gif" border="0" |;
		print qq| align="middle" hspace="10">\n|;
		print qq|$table</a><br>\n|;
	    } # foreach @tablenames
	    print qq|</div>|;

	} # if match $host and $dsn
    } # foreach @dsns 
} # foreach @servers

&endhtml;

sub endhtml {
    print $q -> end_html;
}

sub remotedsn {
    my ($cp) = @_;
    my ($evh, $cnh, $sth, $r);
    my ($r, $sqlstate, $native, $text, $textlen);
    my ($ldsn, $dsnlength, $driver, $driverlength);

    my @dsns;

    $evh =  $cp -> sql_alloc_handle ($SQL_HANDLE_ENV, $SQL_NULL_HANDLE);
    $r = $cp -> 
	sql_set_env_attr ($evh, $SQL_ATTR_ODBC_VERSION, $SQL_OV_ODBC2, 0);

    $cnh = $cp -> sql_alloc_handle ($SQL_HANDLE_DBC, $evh);

    ($r, $sqlstate, $native, $text, $textlen) = 
	$cp -> sql_get_diag_rec ($SQL_HANDLE_ENV, $evh, 1, 255);

    ($r, $ldsn, $dsnlength, $driver, $driverlength) = 
	$cp -> sql_data_sources ($evh, $SQL_FETCH_FIRST, 255, 255);
    push @dsns, ($ldsn);
    while (1) {
	($r, $ldsn, $dsnlength, $driver, $driverlength) = 
	    $cp -> sql_data_sources ($evh, $SQL_FETCH_NEXT, 255, 255);
	last unless $r == $SQL_SUCCESS;
	push @dsns, ($ldsn);
    }

    $r = $cp -> sql_free_handle ($SQL_HANDLE_DBC, $cnh);
    $r = $cp -> sql_free_handle ($SQL_HANDLE_ENV, $evh);

    return @dsns;
}

# Returns Bridge error text, sql_get_diag_rec text or 
# empty string on success.  The peer host logins are 
# looked up in the %peers hash, the DSN logins are from 
# the login form.
sub gettablenames {
    my ($lhost, $ldsn, $ldsnuser, $ldsnpwd) = @_;
    my ($r, $sqlstate, $native, $text, $textlen);
    my ($evh, $cnh, $sth);
    $#tablenames = -1;
    my ($peerusername, $peerpassword) = split /::/, $peers{$lhost};
    my $client = 
	eval { RPC::PlClient->new('peeraddr' => $lhost,
				  'peerport' => $peerport,
				  'application' => 'RPC::PlServer',
				  'version' => $UnixODBC::VERSION,
				  'user' => $peerusername,
				  'password' => $peerpassword) }
    or return 'Bridge client login error.';
    my $c = $client -> ClientObject ('BridgeAPI', 'new');
    if (ref $c ne 'RPC::PlClient::Object::BridgeAPI' ) {
	return 'Could not create bridge client object.';
    }

    $evh =  $c -> sql_alloc_handle ($SQL_HANDLE_ENV, $SQL_NULL_HANDLE);
    if (defined $evh) { 
	$r = $c -> 
	    sql_set_env_attr ($evh, $SQL_ATTR_ODBC_VERSION, $SQL_OV_ODBC2, 0);
    } else {
	($r, $sqlstate, $native, $text, $textlen) = 
	    $c -> sql_get_diag_rec ($SQL_HANDLE_ENV, $evh, 1, 255);
	return $text;
    }

    $cnh = $c -> sql_alloc_handle ($SQL_HANDLE_DBC, $evh);
    if (! defined $cnh) {
	($r, $sqlstate, $native, $text, $textlen) = 
	    $c -> sql_get_diag_rec ($SQL_HANDLE_ENV, $evh, 1, 255);
	return $text;
    }

    $r = $c -> sql_connect ($cnh, $ldsn, length($ldsn),
			$ldsnuser, length($ldsnuser), 
			$ldsnpwd, length($ldsnpwd));
    if ($r != $SQL_SUCCESS) {
	($r, $sqlstate, $native, $text, $textlen) = 
	    $c -> sql_get_diag_rec ($SQL_HANDLE_DBC, $cnh, 1, 255);
	return $text;
    }

    $sth = $c -> sql_alloc_handle ($SQL_HANDLE_STMT, $cnh);
    if (! defined $sth) {
	($r, $sqlstate, $native, $text, $textlen) = 
	    $c -> sql_get_diag_rec ($SQL_HANDLE_DBC, $cnh, 1, 255);
	return $text;
    }

    $r = $c -> sql_tables ($sth, '', 0, '', 0, '', 0, '', 0);
    if ($r != $SQL_SUCCESS) {
	($r, $sqlstate, $native, $text, $textlen) = 
	    $c -> sql_get_diag_rec ($SQL_HANDLE_STMT, $sth, 1, 255);
	return $text;
    }

    while (1) {
	$r = $c -> sql_fetch ($sth);
	last if $r == $SQL_NO_DATA;
	($r, $text, $textlen) = 
	    $c -> sql_get_data ($sth, 3, $SQL_C_CHAR, 255);
	if ($r != $SQL_SUCCESS) {
	    ($r, $sqlstate, $native, $text, $textlen) = 
		$c -> sql_get_diag_rec ($SQL_HANDLE_STMT, $sth, 1, 255);
	    return $text;
	} 
	push @tablenames, ($text);
    }

    $r = $c -> sql_free_handle ($SQL_HANDLE_STMT, $sth);
    if ($r != $SQL_SUCCESS) {
	($r, $sqlstate, $native, $text, $textlen) = 
	    $c -> sql_get_diag_rec ($SQL_HANDLE_STMT, $sth, 1, 255);
	return $text;
    }

    $r = $c -> sql_disconnect ($cnh);
    if ($r != $SQL_SUCESS) {
	($r, $sqlstate, $native, $text, $textlen) = 
	    $c -> sql_get_diag_rec ($SQL_HANDLE_DBC, $cnh, 1, 255);
	return $text;
    }

    $r = $c -> sql_free_connect ($cnh);
    if ($r != $SQL_SUCESS) {
	($r, $sqlstate, $native, $text, $textlen) = 
	    $c -> sql_get_diag_rec ($SQL_HANDLE_DBC, $cnh, 1, 255);
	return $text;
    }

    $r = $c -> sql_free_handle ($SQL_HANDLE_ENV, $evh);
    if ($r != $SQL_SUCESS) {
	($r, $sqlstate, $native, $text, $textlen) = 
	    $c -> sql_get_diag_rec ($SQL_HANDLE_ENV, $evh, 1, 255);
	return $text;
    }
    return '';
}

sub readlogins {
    open LOGIN, $loginfile or die "Cannot open $loginfile: $!";
    my ($line, $host, $userpwd);
    while (defined ($line = <LOGIN>)) {
	next if $line =~ /^\#/;
	next if $line !~ /.*?::.*?::/;
	($host, $userpwd) = split /::/, $line, 2;
	$peers{$host} = $userpwd;
    }
    close LOGIN;
}
